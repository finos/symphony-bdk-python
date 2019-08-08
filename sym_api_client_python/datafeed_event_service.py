import logging
from .exceptions.UnauthorizedException import UnauthorizedException

#for testing
import json

class DataFeedEventService:

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client
        self.datafeed_id = None
        self.datafeed_events = []
        self.room_listeners = []
        self.im_listeners = []
        self.connection_listeners = []
        self.elements_listeners = []
        self.registered_triggers = []
        self.stop = False
        self.datafeed_client = self.bot_client.get_datafeed_client()

    def start_datafeed(self):
        logging.info('DataFeedEventService/startDataFeed()')
        self.datafeed_id = self.datafeed_client.create_datafeed()
        self.read_datafeed(self.datafeed_id)

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

    def activate_datafeed(self):
        if self.stop:
            self.stop = False

    def deactivate_datafeed(self):
        if not self.stop:
            self.stop = True

    #to be edited
    def register_trigger_pattern(self, pattern_to_match, commands):
        trigger = (pattern_to_match, commands)
        self.registered_triggers.append(trigger)

    #probably want to create separate entity to store action trigger
    def register_trigger_action(self, action, value):
        trigger = (action, value)
        self.registered_triggers.append(trigger)

    def check_message_for_trigger(self, payload):
        #check message for trigger, can pass this function to
        #the event handlers, and then set a local flag based on the value
        logic_matches = []
        if logic_matches:
            return True
        else:
            return False

    # read_datafeed function reads an array of events
    # read_datafeed function reads an array of events coming back from
    # DataFeedClient checks to see that sender's email is not equal to Bot's
    # email in config filemthis functionality helps bot avoid entering an
    # infinite loop where it responds to its own messageSent
    # after an event comes back over the dataFeed, the json object returned
    # from read_datafeed() gets passed to handle_event()
    def read_datafeed(self, datafeed_id):
        while not self.stop:
            try:
                data = self.datafeed_client.read_datafeed(datafeed_id)
                if data:
                    events = data[0]
                    logging.debug(
                        'DataFeedEventService/read_datafeed() --> '
                        'Incoming data from read_datafeed(): {}'.format(json.dumps(events[0]['payload'], indent=4)
                            )
                    )
                    for event in events:
                        #consider adding a debug flag for demos/testing
                        #print(json.dumps(event, indent=4))
                        if event['initiator']['user']['userId'] != \
                                self.bot_client.get_bot_user_info()['id']:
                            self.handle_event(event)
                else:
                    logging.debug(
                        'DataFeedEventService() - no data coming in from '
                        'datafeed --> read_datafeed()'
                    )

            except UnauthorizedException:
                logging.debug(
                    'DataFeedEventService - caught unauthorized exception '
                    '--> startDataFeed()'
                )
                self.start_datafeed()

    # function takes in single event --> Checks eventType --> forwards event
    # to proper handling function there is a handle_event function that
    # corresponds to each eventType
    def handle_event(self, payload):
        logging.debug('DataFeedEventService/handle_event()')
        event_type = str(payload['type'])
        if event_type == 'MESSAGESENT':
            self.msg_sent_handler(payload)
        elif event_type == 'INSTANTMESSAGECREATED':
            self.instant_msg_handler(payload)
        elif event_type == 'ROOMCREATED':
            self.room_created_handler(payload)
        elif event_type == 'ROOMDEACTIVATED':
            self.room_deactivated_handler(payload)
        elif event_type == 'ROOMREACTIVATED':
            self.room_reactivated_handler(payload)
        elif event_type == 'USERJOINEDROOM':
            self.user_joined_room_handler(payload)
        elif event_type == 'USERLEFTROOM':
            self.user_left_room_handler(payload)
        elif event_type == 'ROOMMEMBERPROMOTEDTOOWNER':
            self.promoted_to_owner(payload)
        elif event_type == 'ROOMMEMBERDEMOTEDFROMOWNER':
            self.demoted_to_owner(payload)
        elif event_type == 'CONNECTIONACCEPTED':
            self.connection_accepted_handler(payload)
        elif event_type == 'CONNECTIONREQUESTED':
            self.connection_requested_handler(payload)
        elif event_type == 'SYMPHONYELEMENTSACTION':
            self.elements_action_handler(payload)
        else:
            logging.debug('no event detected')
            return

    # check streamType --> send data to appropriate listener
    def msg_sent_handler(self, payload):
        logging.debug('msg_sent_handler function started')
        stream_type = payload['payload']['messageSent']['message']['stream']['streamType']
        message_sent_data = payload['payload']['messageSent']['message']
        if str(stream_type) == 'ROOM':
            for listener in self.room_listeners:
                listener.on_room_msg(message_sent_data)
        else:
            for listener in self.im_listeners:
                listener.on_im_message(message_sent_data)

    def instant_msg_handler(self, payload):
        logging.debug('instant_msg_handler function started')
        instant_message_data = payload['payload']['instantMessageCreated']
        for listener in self.im_listeners:
            listener.on_im_created(instant_message_data)

    def room_created_handler(self, payload):
        logging.debug('room_created_handler function started')
        room_created_data = payload['payload']['roomCreated']
        for listener in self.room_listeners:
            listener.on_room_created(room_created_data)

    def room_updated_handler(self, payload):
        logging.debug('room_updated_handler')
        room_updated_data = payload['payload']['roomUpdated']
        for listener in self.room_listeners:
            listener.on_room_updated(room_updated_data)

    def room_deactivated_handler(self, payload):
        logging.debug('room_deactivated_handler')
        room_deactivated_data = payload['payload']['roomDeactivated']
        for listener in self.room_listeners:
            listener.on_room_deactivated(room_deactivated_data)

    def room_reactivated_handler(self, payload):
        logging.debug('room_reactivated_handler')
        room_reactivated_data = payload['payload']['roomReactivated']
        for listener in self.room_listeners:
            listener.on_room_reactivated(room_reactivated_data)

    def user_joined_room_handler(self, payload):
        logging.debug('user_joined_room_handler')
        user_joined_room_data = payload['payload']['userJoinedRoom']
        for listener in self.room_listeners:
            listener.on_user_joined_room(user_joined_room_data)

    def user_left_room_handler(self, payload):
        logging.debug('user_left_room_handler')
        user_left_room_data = payload['payload']['userLeftRoom']
        for listener in self.room_listeners:
            listener.on_user_left_room(user_left_room_data)

    def promoted_to_owner(self, payload):
        logging.debug('promoted_to_owner')
        promoted_to_owner_data = payload['payload']['roomMemberPromotedToOwner']
        for listener in self.room_listeners:
            listener.on_room_member_promoted_to_owner(promoted_to_owner_data)

    def demoted_to_owner(self, payload):
        logging.debug('demoted_to_Owner')
        demoted_to_owner_data = payload['payload']['roomMemberDemotedFromOwner']
        for listener in self.room_listeners:
            listener.on_room_member_demoted_from_owner(demoted_to_owner_data)

    def connection_accepted_handler(self, payload):
        logging.debug('connection_accepted_handler')
        connection_accepted_data = payload['payload']['connectionAccepted']
        for listener in self.connection_listeners:
            listener.on_connection_accepted(connection_accepted_data)

    def connection_requested_handler(self, payload):
        logging.debug('connection_requested_handler')
        connection_requested_data = payload['payload']['connectionRequested']
        for listener in self.connection_listeners:
            listener.on_connection_requested(connection_requested_data)

    def elements_action_handler(self, payload):
        logging.debug('elements_action_handler')
        elements_action_data = payload['payload']['symphonyElementsAction']
        for listener in self.elements_listeners:
            listener.on_elements_action(elements_action_data)
