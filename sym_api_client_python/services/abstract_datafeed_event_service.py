from abc import ABC, abstractmethod
import logging

from .datafeed_id_repository import OnDiskDatafeedIdRepository
from ..listeners.elements_listener import ElementsActionListener
from ..listeners.connection_listener import ConnectionListener
from ..listeners.im_listener import IMListener
from ..listeners.room_listener import RoomListener

from ..auth.auth_endpoint_constants import auth_endpoint_constants

log = logging.getLogger(__name__)


class AbstractDatafeedEventService(ABC):

    def __init__(self, sym_bot_client, error_timeout_sec=None, maximum_timeout_sec=None):
        self.datafeed_events = []
        self.room_listeners = []
        self.im_listeners = []
        self.connection_listeners = []
        self.elements_listeners = []
        self.suppression_listeners = []
        self.wall_post_listeners = []
        self.registered_triggers = []

        self.bot_client = sym_bot_client
        self.config = sym_bot_client.get_sym_config()
        self.datafeed_client = self.bot_client.get_datafeed_client()
        self.datafeed_id_repository = OnDiskDatafeedIdRepository(self.config.get_datafeed_id_folder_path())
        self.stop = False

        # TODO: Should not be handled in the DF ES like this, why put a timeout in the config if we can put a parameter with default value(config related)
        # Timeout will start at and eventually reset to this
        _config_key = 'datafeedEventsErrorTimeout'
        # Mapping of Event type to the function to handle it
        self.routing_dict = {
            'MESSAGESENT': self.msg_sent_handler,
            'MESSAGESUPPRESSED': self.suppressed_message_handler,
            'INSTANTMESSAGECREATED': self.instant_msg_handler,
            'ROOMCREATED': self.room_created_handler,
            'ROOMDEACTIVATED': self.room_deactivated_handler,
            'ROOMREACTIVATED': self.room_reactivated_handler,
            'ROOMUPDATED': self.room_updated_handler,
            'USERJOINEDROOM': self.user_joined_room_handler,
            'USERLEFTROOM': self.user_left_room_handler,
            'ROOMMEMBERPROMOTEDTOOWNER': self.promoted_to_owner,
            'ROOMMEMBERDEMOTEDFROMOWNER': self.demoted_from_owner,
            'CONNECTIONACCEPTED': self.connection_accepted_handler,
            'CONNECTIONREQUESTED': self.connection_requested_handler,
            'SYMPHONYELEMENTSACTION': self.elements_action_handler,
            'SHAREDPOST': self.shared_post_handler,
        }

        if error_timeout_sec is None:
            self.baseline_timeout_sec = self.config.data.get(_config_key, auth_endpoint_constants["TIMEOUT"])
        else:
            if _config_key in self.config.data:
                log.debug('{} listed in config, but overriden to {}s by parammeter'
                         .format(_config_key, error_timeout_sec))
            self.baseline_timeout_sec = error_timeout_sec

        self.current_timeout_sec = self.baseline_timeout_sec
        # Never wait less than this
        self.lower_threshold = self.baseline_timeout_sec
        # Raise a RuntimeError once this upper threshold exceeded
        if maximum_timeout_sec is None:
            self.upper_threshold = self.config.data.get('datafeedEventsErrorMaxTimeout', 60)
        else:
            self.upper_threshold = maximum_timeout_sec
        # After every failure multiply the timeout by a factor
        self.timeout_multiplier = 2

    @abstractmethod
    def start_datafeed(self):
        pass

    def activate_datafeed(self):
        if self.stop:
            self.stop = False

    def deactivate_datafeed(self):
        if not self.stop:
            self.stop = True

    ### Listeners ###
    def add_listeners(self, *listeners):
        for listener in listeners:
            if isinstance(listener, ElementsActionListener):
                self.add_elements_listener(listener)
            elif isinstance(listener, ConnectionListener):
                self.add_connection_listener(listener)
            elif isinstance(listener, IMListener):
                self.add_im_listener(listener)
            elif isinstance(listener, RoomListener):
                self.add_room_listener(listener)

    def remove_listeners(self, *listeners):
        for listener in listeners:
            if isinstance(listener, ElementsActionListener):
                self.remove_elements_listener(listener)
            elif isinstance(listener, ConnectionListener):
                self.remove_connection_listener(listener)
            elif isinstance(listener, IMListener):
                self.remove_im_listener(listener)
            elif isinstance(listener, RoomListener):
                self.remove_room_listener(listener)

    def add_room_listener(self, room_listener):
        self.room_listeners.append(room_listener)

    def remove_room_listener(self, room_listener):
        self.room_listeners.remove(room_listener)

    def add_im_listener(self, im_listener):
        self.im_listeners.append(im_listener)

    def remove_im_listener(self, im_listener):
        self.im_listeners.remove(im_listener)

    def add_connection_listener(self, connection_listener):
        self.connection_listeners.append(connection_listener)

    def remove_connection_listener(self, connection_listener):
        self.connection_listeners.remove(connection_listener)

    def add_elements_listener(self, elements_listener):
        self.elements_listeners.append(elements_listener)

    def remove_elements_listener(self, elements_listener):
        self.elements_listeners.remove(elements_listener)

    def add_wall_post_listener(self, wall_post_listener):
        self.wall_post_listeners.append(wall_post_listener)

    def remove_wall_post_listener(self, wall_post_listener):
        self.wall_post_listeners.remove(wall_post_listener)

    def add_suppression_listener(self, suppression_listener):
        self.suppression_listeners.append(suppression_listener)

    def remove_suppression_listener(self, suppression_listener):
        self.suppression_listeners.remove(suppression_listener)


    # TODO: Add doc
    # TODO: Change all brackets access types by get function
    def handle_events(self, events):
        """ Routes the event to the proper handler.

            Also Checks to see that the sender's email is not equal to Bot's email in config file.
            This functionality helps the bot avoid entering an infinite loop where it responds to its own messageSent
            after an event comes back over the dataFeed
        """
        log.debug('DataFeedEventService/handle_events()')
        for event in events:
            if event is None:
                continue
            
            log.debug(
                'DataFeedEventService/read_datafeed() --> '
                'Incoming event with id: {}'.format(event.get('id'))
            )
            
            if event['initiator']['user']['userId'] == self.bot_client.get_bot_user_info()['id']:
                continue
            else:
                self.handle_event(event)

    # function takes in single event --> Checks eventType --> forwards event
    # to proper handling function there is a handle_event function that
    # corresponds to each eventType
    def handle_event(self, payload):
        log.debug('DataFeedEventService/handle_event()')
        event_type = str(payload['type'])
        try:
            route = self.routing_dict[event_type]
        except KeyError:
            log.error('Unrecognised event type: ' + event_type)
            return

        route(payload)

    ### Handlers ###
    def msg_sent_handler(self, payload):
        """This handler is used for both room messages and IMs. Which listener is invoked
        depends on the streamType"""
        log.debug('msg_sent_handler function started')
        stream_type = payload['payload']['messageSent']['message']['stream']['streamType']
        message_sent_data = payload['payload']['messageSent']['message']
        if str(stream_type) == 'ROOM':
            for listener in self.room_listeners:
                listener.on_room_msg(message_sent_data)
        elif str(stream_type) == 'POST':
            for listener in self.wall_post_listeners:
                listener.on_wall_post_msg(message_sent_data)
        else:
            for listener in self.im_listeners:
                listener.on_im_message(message_sent_data)

    def instant_msg_handler(self, payload):
        log.debug('instant_msg_handler function started')
        instant_message_data = payload['payload']['instantMessageCreated']
        for listener in self.im_listeners:
            listener.on_im_created(instant_message_data)

    def room_created_handler(self, payload):
        log.debug('room_created_handler function started')
        room_created_data = payload['payload']['roomCreated']
        for listener in self.room_listeners:
            listener.on_room_created(room_created_data)

    def room_updated_handler(self, payload):
        log.debug('room_updated_handler')
        room_updated_data = payload['payload']['roomUpdated']
        for listener in self.room_listeners:
            listener.on_room_updated(room_updated_data)

    def room_deactivated_handler(self, payload):
        log.debug('room_deactivated_handler')
        room_deactivated_data = payload['payload']['roomDeactivated']
        for listener in self.room_listeners:
            listener.on_room_deactivated(room_deactivated_data)

    def room_reactivated_handler(self, payload):
        log.debug('room_reactivated_handler')
        room_reactivated_data = payload['payload']['roomReactivated']
        for listener in self.room_listeners:
            listener.on_room_reactivated(room_reactivated_data)

    def user_joined_room_handler(self, payload):
        log.debug('user_joined_room_handler')
        user_joined_room_data = payload['payload']['userJoinedRoom']
        for listener in self.room_listeners:
            listener.on_user_joined_room(user_joined_room_data)

    def user_left_room_handler(self, payload):
        log.debug('user_left_room_handler')
        user_left_room_data = payload['payload']['userLeftRoom']
        for listener in self.room_listeners:
            listener.on_user_left_room(user_left_room_data)

    def promoted_to_owner(self, payload):
        log.debug('promoted_to_owner')
        promoted_to_owner_data = payload['payload']['roomMemberPromotedToOwner']
        for listener in self.room_listeners:
            listener.on_room_member_promoted_to_owner(promoted_to_owner_data)

    def demoted_from_owner(self, payload):
        log.debug('demoted_from_owner')
        demoted_from_owner_data = payload['payload']['roomMemberDemotedFromOwner']
        for listener in self.room_listeners:
            listener.on_room_member_demoted_from_owner(demoted_from_owner_data)

    def connection_accepted_handler(self, payload):
        log.debug('connection_accepted_handler')
        connection_accepted_data = payload['payload']['connectionAccepted']
        for listener in self.connection_listeners:
            listener.on_connection_accepted(connection_accepted_data)

    def connection_requested_handler(self, payload):
        log.debug('connection_requested_handler')
        connection_requested_data = payload['payload']['connectionRequested']
        for listener in self.connection_listeners:
            listener.on_connection_requested(connection_requested_data)

    def elements_action_handler(self, payload):
        log.debug('elements_action_handler')
        for listener in self.elements_listeners:
            listener.on_elements_action(payload)

    def shared_post_handler(self, payload):
        log.debug('shared_post_handler')
        shared_post = payload['payload']['sharedPost']
        for listener in self.wall_post_listeners:
            listener.on_shared_post(shared_post)

    def suppressed_message_handler(self, payload):
        log.debug('suppressed_message_handler')
        message_suppressed = payload['payload']['messageSuppressed']
        for listener in self.suppression_listeners:
            listener.on_message_suppression(message_suppressed)

    ### Handle errors ###
    def get_and_increase_timeout(self, previous_exc=None):
        """Return the current timeout and then increase it for next time. Throw RuntimeError if the
        current timeout is larger than the upper threshold - if one exists.

            previous_exc: provide the exception that causes the original timeout to have that
                          attached to the stacktrace of the runtime error, showing more clearly
                          why the timeout occurred. """

        if (self.upper_threshold is not None) and (self.current_timeout_sec > self.upper_threshold):
            e = RuntimeError(
                'Upper timeout threshold exceeded: {:.4g}s'.format(self.upper_threshold)
            )
            if previous_exc is not None:
                raise e from previous_exc
            else:
                raise e
        else:
            original = self.current_timeout_sec
            new_timeout = original * self.timeout_multiplier
            self.current_timeout_sec = new_timeout
            log.debug('DataFeedEventService/get_and_increase_timeout --> '
                      'Using current timeout of {:.4g}s, but increasing to {:.4g}s for next time'
                      .format(original, new_timeout))
            return max(self.lower_threshold, original)

    def decrease_timeout(self):
        original = self.current_timeout_sec
        new_timeout = self.baseline_timeout_sec
        if original != new_timeout:
            log.debug('DataFeedEventService/decrease_timeout() --> '
                      'Decreasing timeout from {:.4g}s to {:.4g}s'.format(original, new_timeout))
            self.current_timeout_sec = new_timeout
        return self.current_timeout_sec

    def _get_from_file_or_create_datafeed_id(self):
        if self.config.should_store_datafeed_id():
            datafeed_id = self.datafeed_id_repository.read_datafeed_id_from_file()
            if datafeed_id:
                return datafeed_id
        return self._create_datafeed_and_persist()

    def _create_datafeed_and_persist(self):
        datafeed_id = self.datafeed_client.create_datafeed()
        if self.config.should_store_datafeed_id():
            self.datafeed_id_repository.store_datafeed_id_to_file(datafeed_id, self.config.get_agent_url())
        return datafeed_id
