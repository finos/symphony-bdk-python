from abc import ABC, abstractmethod
from typing import List

from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.auth.auth_session import AuthSession

from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.gen.agent_model.v4_event import V4Event


class DatafeedLoop(ABC):
    """Interface for a loop service to be used for handling the datafeed API.
    """

    @abstractmethod
    def start(self):
        """Start the datafeed event service"""
        pass

    @abstractmethod
    def stop(self):
        """Stop the datafeed event service"""
        pass

    @abstractmethod
    def subscribe(self, listener: RealTimeEventListener):
        """The bot subscribes to a RealTimeEventListener

        :param listener: RealTimeEventListener a Datafeed event listener to be subscribed
        """
        pass

    @abstractmethod
    def unsubscribe(self, listener: RealTimeEventListener):
        """The bot unsubscribes to a RealtimeEventListener

        :param listener: RealTimeEventListener a Datafeed event listener to be subscribed
        """
        pass


class AbstractDatafeedLoop(DatafeedLoop, ABC):
    """Base class for implementing the datafeed services.

    A datafeed services can help a bot subscribe or unsubscribe to a RealTimeEventListener and handle the received
    event by the subscribed listeners.
    """

    def __init__(self, datafeed_api: DatafeedApi, auth_session: AuthSession, config: BdkConfig):
        self.datafeed_api = datafeed_api
        self.listeners = []
        self.auth_session = auth_session
        self.bdk_config = config
        self.api_client = datafeed_api.api_client
        self.dispatch_dict = {
            'MESSAGESENT': ('on_message_sent', 'message_sent'),
            'SHAREDPOST': ('on_shared_post', 'shared_post'),
            'INSTANTMESSAGECREATED': ('on_instant_message_created', 'instant_message_created'),
            'ROOMCREATED': ('on_room_created', 'room_created'),
            'ROOMUPDATED': ('on_room_updated', 'room_updated'),
            'ROOMDEACTIVATED': ('on_room_deactivated', 'room_deactivated'),
            'ROOMREACTIVATED': ('on_room_reactivated', 'room_reactivated'),
            'USERREQUESTEDTOJOINROOM': ('on_user_requested_to_join_room', 'user_requested_to_join_room'),
            'USERJOINEDROOM': ('on_user_joined_room', 'user_joined_room'),
            'USERLEFTROOM': ('on_user_left_room', 'user_left_room'),
            'ROOMMEMBERPROMOTEDTOOWNER': ('on_room_member_promoted_to_owner', 'room_member_promoted_to_owner'),
            'ROOMMEMBERDEMOTEDFROMOWNER': ('on_room_demoted_from_owner', 'room_member_demoted_from_owner'),
            'CONNECTIONREQUESTED': ('on_connection_requested', 'connection_requested'),
            'CONNECTIONACCEPTED': ('on_connection_accepted', 'connection_accepted'),
            'SYMPHONYELEMENTSACTION': ('on_symphony_elements_action', 'symphony_elements_action'),
            'MESSAGESUPPRESSED': ('on_message_suppressed', 'message_suppressed')}

    def subscribe(self, listener):
        self.listeners.append(listener)

    def unsubscribe(self, listener):
        self.listeners.remove(listener)

    def handle_v4_event_list(self, events: List[V4Event]):
        for event in events:
            for listener in self.listeners:
                if listener.is_accepting_event(event, self.bdk_config.bot.username):
                    self.dispatch_on_event_type(listener, event)

    def dispatch_on_event_type(self, listener: RealTimeEventListener, event: V4Event):
        try:
            listener_method_name, payload_field_name = self.dispatch_dict[event.type]
            listener_method = getattr(listener, listener_method_name)
            listener_method(event.initiator, getattr(event.payload, payload_field_name))
        except AttributeError as e:
            print(f"Attribute error while dispatching the {event}. {e}")
            raise
        except KeyError:
            print(f"Received event with an unknown type: {event.type}")
