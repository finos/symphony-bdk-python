"""This module gathers all base classes related to the datafeed loop and real time events."""

import asyncio
import logging
from abc import ABC, abstractmethod
from asyncio import Task
from contextvars import ContextVar
from enum import Enum
from typing import List

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_model.v4_event import V4Event

logger = logging.getLogger(__name__)

event_listener_context = ContextVar("event_listener_context", default="main-task")


class DatafeedVersion(Enum):
    """Enum of all possible datafeed versions."""

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
    ROOMMEMBERPROMOTEDTOOWNER = (
        "on_room_member_promoted_to_owner",
        "room_member_promoted_to_owner",
    )
    ROOMMEMBERDEMOTEDFROMOWNER = ("on_room_demoted_from_owner", "room_member_demoted_from_owner")
    CONNECTIONREQUESTED = ("on_connection_requested", "connection_requested")
    CONNECTIONACCEPTED = ("on_connection_accepted", "connection_accepted")
    SYMPHONYELEMENTSACTION = ("on_symphony_elements_action", "symphony_elements_action")
    MESSAGESUPPRESSED = ("on_message_suppressed", "message_suppressed")


def _set_context_var(current_task, event, listener):
    event_id = getattr(event, "id", "None")
    event_listener_context.set(f"{current_task.get_name()}/{event_id}/{id(listener)}")


class AbstractDatafeedLoop(ABC):
    """Base class for implementing the datafeed services.

    A datafeed services can help a bot subscribe or unsubscribe to a RealTimeEventListener and handle the received
    event by the subscribed listeners.
    """

    def __init__(
        self,
        datafeed_api: DatafeedApi,
        session_service: SessionService,
        auth_session: AuthSession,
        config: BdkConfig,
    ):
        """

        :param datafeed_api: DatafeedApi to request the service
        :param session_service: the SessionService to get user session information
        :param auth_session: the AuthSession instance used to get session and key manager tokens
        :param config: the bot configuration
        """
        self._datafeed_api = datafeed_api
        self._session_service = session_service
        self._listeners = []
        self._auth_session = auth_session
        self._api_client = datafeed_api.api_client
        self._running = False
        self._hard_kill = False
        self._timeout = None
        self._tasks = []
        self._retry_config = config.datafeed.retry
        self._bot_info = None

    @abstractmethod
    async def start(self):
        """Start the datafeed event service

        :return: None
        """
        try:
            await self._run_loop()
        finally:
            await self._stop_listener_tasks()

    async def stop(self, hard_kill: bool = False, timeout: float = None):
        """Stop the datafeed event service

        :param hard_kill: if set to True, tasks running listener methods will be cancelled immediately. Otherwise, tasks
          will be awaited until completion.
        :param timeout: timeout in seconds to wait for tasks completion when loop stops.
          None means wait until completion. Ignored if hard_kill set to True.
        :return: None
        """
        self._hard_kill = hard_kill
        self._timeout = timeout
        self._running = False

    def subscribe(self, listener: RealTimeEventListener):
        """Subscribes a new listener to the datafeed loop instance.

        :param listener: the RealTimeEventListener to be added.
        """
        self._listeners.append(listener)

    def unsubscribe(self, listener: RealTimeEventListener):
        """Removes a given listener from the datafeed loop instance.

        :param listener: the RealTimeEventListener to be removed.
        """
        self._listeners.remove(listener)

    async def _run_loop(self):
        self._running = True
        while self._running:
            await self._run_loop_iteration()

    @abstractmethod
    async def _run_loop_iteration(self):
        """Method called while the datafeed loop is running (.i.e stop() is called).
        This should include the logic to read events from the datafeed and dispatch them to the listeners.

        :return: None
        """

    async def _stop_listener_tasks(self):
        if self._hard_kill:
            await self._cancel_tasks()
        else:
            await self._wait_for_completion_or_timeout()

    async def _cancel_tasks(self):
        logger.debug("Cancelling %s listener tasks", len(self._tasks))
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def _wait_for_completion_or_timeout(self):
        logger.debug("Waiting for %s listener tasks to finish", len(self._tasks))
        try:
            await asyncio.wait_for(asyncio.gather(*self._tasks), timeout=self._timeout)
        except asyncio.TimeoutError:
            logger.debug("Task completion timed out")

    async def _run_listener_tasks(self, events: List[V4Event]) -> List[Task]:
        tasks = await self._create_listener_tasks(events)
        if tasks:
            done, _ = await asyncio.wait(tasks)
            return done
        return []

    async def _create_listener_tasks(self, events: List[V4Event]) -> List[Task]:
        tasks = []
        sanitized_events = filter(lambda e: e is not None, events) if events else []

        for event in sanitized_events:
            for listener in self._listeners:
                if await listener.is_accepting_event(event, self._bot_info):
                    task = asyncio.create_task(self._dispatch_to_listener_method(listener, event))
                    tasks.append(task)

        return tasks

    async def _dispatch_to_listener_method(self, listener: RealTimeEventListener, event: V4Event):
        current_task = asyncio.current_task()
        _set_context_var(current_task, event, listener)

        self._tasks.append(current_task)
        try:
            await self._run_listener_method(listener, event)
        finally:
            self._tasks.remove(current_task)

    @staticmethod
    async def _run_listener_method(listener: RealTimeEventListener, event: V4Event):
        try:
            listener_method_name, payload_field_name = RealTimeEvent[event.type].value
        except KeyError:
            logger.info("Received event with an unknown type: %s", event.type)
            return

        listener_method = getattr(listener, listener_method_name)
        event_field = getattr(event.payload, payload_field_name)

        await listener_method(event.initiator, event_field)
