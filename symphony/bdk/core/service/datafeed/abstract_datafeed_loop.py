"""This module gathers all base classes related to the datafeed loop and real time events.
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import List

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_model.v4_event import V4Event

logger = logging.getLogger(__name__)


class DatafeedVersion(Enum):

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

    @abstractmethod
    async def start(self):
        """Start the datafeed event service"""

    @abstractmethod
    async def stop(self):
        """Stop the datafeed event service"""

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

    async def handle_v4_event_list(self, events: List[V4Event]):
        """Handles the event list received from the read datafeed endpoint.
        Calls each listeners for each received events.

        :param events: the list of the received datafeed events.
        """
        for event in filter(lambda e: e is not None, events):
            for listener in self.listeners:
                if await listener.is_accepting_event(event, self.bdk_config.bot.username):
                    await self._dispatch_on_event_type(listener, event)

    async def _dispatch_on_event_type(self, listener: RealTimeEventListener, event: V4Event):
        try:
            listener_method_name, payload_field_name = RealTimeEvent[event.type].value
        except KeyError:
            logger.info("Received event with an unknown type: %s", event.type)
            return

        listener_method = getattr(listener, listener_method_name)
        event_field = getattr(event.payload, payload_field_name)

        await listener_method(event.initiator, event_field)
