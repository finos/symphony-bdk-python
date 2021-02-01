from abc import ABC, abstractmethod
from typing import List

from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.auth.auth_session import AuthSession

from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.core.datafeed.real_time_event_listener import RealTimeEventListener
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
    def __init__(self, datafeed_api: DatafeedApi, auth_session: AuthSession, config: BdkConfig):
        self.datafeed_api = datafeed_api
        self.listeners = []
        self.auth_session = auth_session
        self.bdk_config = config
        self.api_client = datafeed_api.api_client
        self.dispatch_dict = {
            'MESSAGESENT': ('on_message_sent', 'message_sent')
        }

    def subscribe(self, listener):
        self.listeners.append(listener)

    def unsubscribe(self, listener):
        self.listeners.remove(listener)

    def handle_v4_event_list(self, events: List[V4Event]):
        for event in events:
            if event.type is None:  # should we ever check this ? Isn't the generated code supposed to check for nullity or not the right type and raise an exception
                continue
            for listener in self.listeners:
                if listener.is_accepting_event(event, self.bdk_config.bot.username):
                    self.dispatch_on_event_type(listener, event)

    def dispatch_on_event_type(self, listener: RealTimeEventListener, event: V4Event):
        try:
            listener_method_name, payload_field_name = self.dispatch_dict[event.type]
            listener_method = getattr(listener, listener_method_name)
            listener_method(event.initiator, getattr(event.payload, payload_field_name))
        except KeyError:
            print(f"Received event with an unknown type: {event.type}")

    def handle_event(self, event: V4Event):
        # try:
        #     event.type
        pass
