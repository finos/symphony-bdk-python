"""This module gathers all base classes related to the datafeed loop and real time events.
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from contextvars import ContextVar
from enum import Enum
from typing import List

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.gen import ApiException
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_model.v4_event import V4Event

logger = logging.getLogger(__name__)

event_listener_context = ContextVar("event_listener_context", default="main-task")


class DatafeedVersion(Enum):
    """Enum of all possible datafeed versions.
    """
    V1 = "v1"
    V2 = "v2"


class RealTimeEvent(Enum):
    """This enum lists all possible
    `Real Time Events <https://docs.developers.symphony.com/building-bots-on-symphony/datafeed/real-time-events>`_
    received from the datafeed loop.

    Enum field name is the maps the exact value of field type in the datafeed payload.
    First element in enum value corresponds to the listener method who should be called when given event is received.
    Second element in enum value corresponds to the field name of event in the received payload.
    """
    MESSAGESENT = ("on_message_sent", "message_sent")
    SHAREDPOST = ("on_shared_post", "shared_post")
    INSTANTMESSAGECREATED = ("on_instant_message_created", "instant_message_created")
    ROOMCREATED = ("on_room_created", "room_created")
    ROOMUPDATED = ("on_room_updated", "room_updated")
    ROOMDEACTIVATED = ("on_room_deactivated", "room_deactivated")
    ROOMREACTIVATED = ("on_room_reactivated", "room_reactivated")
    USERREQUESTEDTOJOINROOM = ("on_user_requested_to_join_room", "user_requested_to_join_room")
    USERJOINEDROOM = ("on_user_joined_room", "user_joined_room")
    USERLEFTROOM = ("on_user_left_room", "user_left_room")
    ROOMMEMBERPROMOTEDTOOWNER = ("on_room_member_promoted_to_owner", "room_member_promoted_to_owner")
    ROOMMEMBERDEMOTEDFROMOWNER = ("on_room_demoted_from_owner", "room_member_demoted_from_owner")
    CONNECTIONREQUESTED = ("on_connection_requested", "connection_requested")
    CONNECTIONACCEPTED = ("on_connection_accepted", "connection_accepted")
    SYMPHONYELEMENTSACTION = ("on_symphony_elements_action", "symphony_elements_action")
    MESSAGESUPPRESSED = ("on_message_suppressed", "message_suppressed")


class AbstractDatafeedLoop(ABC):
    """Base class for implementing the datafeed services.

    A datafeed services can help a bot subscribe or unsubscribe to a RealTimeEventListener and handle the received
    event by the subscribed listeners.
    """

    def __init__(self, datafeed_api: DatafeedApi, auth_session: AuthSession, config: BdkConfig):
        """

        :param datafeed_api: The file location of the spreadsheet
        :type auth_session: the AuthSession instance used to get session and key manager tokens
        :param config: the bot configuration
        """
        self.datafeed_api = datafeed_api
        self.listeners = []
        self.auth_session = auth_session
        self.bdk_config = config
        self.api_client = datafeed_api.api_client
        self.running = False
        self.hard_kill = False
        self.timeout = None
        self.tasks = []

    async def start(self):
        """Start the datafeed event service

        :return: None
        """
        logger.debug("Starting datafeed loop")

        await self.prepare_datafeed()
        try:
            await self._run_loop()
        finally:
            logger.debug("Stopping datafeed loop")
            await self._stop_listener_tasks()

    async def stop(self, hard_kill: bool = False, timeout: float = None):
        """Stop the datafeed event service

        :param hard_kill: if set to True, tasks running listener methods will be cancelled immediately. Otherwise, tasks
          will be awaited until completion.
        :param timeout: timeout in seconds to wait for tasks completion when loop stops.
          None means wait until completion. Ignored if hard_kill set to True.
        :return: None
        """
        self.hard_kill = hard_kill
        self.timeout = timeout
        self.running = False

    @abstractmethod
    async def prepare_datafeed(self):
        """Method called when :py:meth:`start` is called and before datafeed loop is actually running

        :return: None
        """

    @abstractmethod
    async def read_datafeed(self) -> List[V4Event]:
        """Method called inside :py:meth:`start` while datafeed loop is actually running

        :return: the list of V4Event elements received
        """

    @abstractmethod
    async def recreate_datafeed(self):
        """Method called when datafeed is stale and needs to be recreated (i.e. :py:meth:`read_datafeed` raises an
        ApiException with status 400)

        :return: None
        """

    def subscribe(self, listener: RealTimeEventListener):
        """Subscribes a new listener to the datafeed loop instance.

        :param listener: the RealTimeEventListener to be added.
        """
        self.listeners.append(listener)

    def unsubscribe(self, listener: RealTimeEventListener):
        """Removes a given listener from the datafeed loop instance.

        :param listener: the RealTimeEventListener to be removed.
        """
        self.listeners.remove(listener)

    async def _run_loop(self):
        self.running = True
        while self.running:
            await self._run_loop_iteration()

    async def _run_loop_iteration(self):
        try:
            event_list = await self.read_datafeed()
            await self.handle_v4_event_list(event_list)
        except ApiException as exc:
            if exc.status == 400:
                await self.recreate_datafeed()
            else:
                raise exc

    async def _stop_listener_tasks(self):
        if self.hard_kill:
            await self._cancel_tasks()
        else:
            await self._wait_for_completion_or_timeout()

    async def _cancel_tasks(self):
        logger.debug("Cancelling %s listener tasks", len(self.tasks))
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)

    async def _wait_for_completion_or_timeout(self):
        logger.debug("Waiting for %s listener tasks to finish", len(self.tasks))
        try:
            await asyncio.wait_for(asyncio.gather(*self.tasks), timeout=self.timeout)
        except asyncio.TimeoutError:
            logger.debug("Task completion timed out")

    async def handle_v4_event_list(self, events: List[V4Event]):
        """Handles the event list received from the read datafeed endpoint.
        Calls each listeners for each received events.

        :param events: the list of the received datafeed events.
        """
        if not events:
            return

        for event in filter(lambda e: e is not None, events):
            for listener in self.listeners:
                if await listener.is_accepting_event(event, self.bdk_config.bot.username):
                    asyncio.create_task(self._dispatch_to_listener_method(listener, event))

    async def _dispatch_to_listener_method(self, listener: RealTimeEventListener, event: V4Event):
        current_task = asyncio.current_task()
        self._set_context_var(current_task, event, listener)

        self.tasks.append(current_task)
        try:
            await self._run_listener_method(listener, event)
        finally:
            self.tasks.remove(current_task)

    def _set_context_var(self, current_task, event, listener):
        event_id = getattr(event, "id", "None")
        event_listener_context.set(f"{current_task.get_name()}/{event_id}/{id(listener)}")

    async def _run_listener_method(self, listener: RealTimeEventListener, event: V4Event):
        try:
            listener_method_name, payload_field_name = RealTimeEvent[event.type].value
        except KeyError:
            logger.info("Received event with an unknown type: %s", event.type)
            return

        listener_method = getattr(listener, listener_method_name)
        event_field = getattr(event.payload, payload_field_name)

        await listener_method(event.initiator, event_field)
