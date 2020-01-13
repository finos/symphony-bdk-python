import asyncio
from concurrent.futures import CancelledError
from functools import partial
import json
import logging
import datetime
from collections import namedtuple
import time

from .auth.auth_endpoint_constants import auth_endpoint_constants
from .exceptions.ServerErrorException import ServerErrorException
from .exceptions.UnauthorizedException import UnauthorizedException
from .exceptions.APIClientErrorException import APIClientErrorException
from .exceptions.DatafeedExpiredException import DatafeedExpiredException
from .exceptions.ServerErrorException import ServerErrorException

log = logging.getLogger(__name__)

def make_datetime(unix_timestamp_millis):
    seconds, millis = divmod(unix_timestamp_millis, 1000)
    return datetime.datetime.utcfromtimestamp(seconds).replace(microsecond=millis*1000)

EventTrace = namedtuple('EventTrace', 'message_id creation_time bot_received listeners_complete bot_complete')

class DataFeedEventService:

    def __init__(self, sym_bot_client, log_events=True, error_timeout_sec=None):
        self.bot_client = sym_bot_client
        self.datafeed_id = None
        self.datafeed_events = []
        self.room_listeners = []
        self.im_listeners = []
        self.connection_listeners = []
        self.elements_listeners = []
        self.suppression_listeners = []
        self.wall_post_listeners = []
        self.registered_triggers = []
        self.stop = False
        self.datafeed_client = self.bot_client.get_datafeed_client()
        self.log_events = log_events

        config = self.bot_client.get_sym_config()
        # Timeout will start at and eventually reset to this
        _config_key = 'datafeedEventsErrorTimeout'
        if error_timeout_sec is None:
            self.baseline_timeout_sec = config.data.get(_config_key, auth_endpoint_constants["TIMEOUT"])
        else:

            if _config_key in config.data:
                log.info('{} listed in config, but overriden to {}s by parammeter'
                .format(_config_key, error_timeout_sec))
            self.baseline_timeout_sec = error_timeout_sec

        self.current_timeout_sec = self.baseline_timeout_sec
        # Never wait less than this
        self.lower_threshold = self.baseline_timeout_sec
        # Raise a RuntimeError once this is exceeded
        self.upper_threshold = None
        # After every failure multiply the timeout by a factor
        self.timeout_multiplier = 2

        # Mapping of Event type to the function to handle it
        self.routing_dict = {
            'MESSAGESENT' : self.msg_sent_handler,
            'MESSAGESUPPRESSED' : self.suppressed_message_handler,
            'INSTANTMESSAGECREATED' : self.instant_msg_handler,
            'ROOMCREATED' : self.room_created_handler,
            'ROOMDEACTIVATED' : self.room_deactivated_handler,
            'ROOMREACTIVATED' : self.room_reactivated_handler,
            'ROOMUPDATED' : self.room_updated_handler,
            'USERJOINEDROOM' : self.user_joined_room_handler,
            'USERLEFTROOM' : self.user_left_room_handler,
            'ROOMMEMBERPROMOTEDTOOWNER' : self.promoted_to_owner,
            'ROOMMEMBERDEMOTEDFROMOWNER' : self.demoted_to_owner,
            'CONNECTIONACCEPTED' : self.connection_accepted_handler,
            'CONNECTIONREQUESTED' : self.connection_requested_handler,
            'SYMPHONYELEMENTSACTION' : self.elements_action_handler,
            'SHAREDPOST': self.shared_post_handler,
        }

    def start_datafeed(self):
        log.info('DataFeedEventService/startDataFeed()')
        self.datafeed_id = self.datafeed_client.create_datafeed()
        self.read_datafeed()

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
        self.wall_post_listeners.remove(self, wall_post_listener)

    def add_suppression_listener(self, suppression_listener):
        self.suppression_listeners.append(suppression_listener)

    def remove_suppression_listener(self, suppression_listener):
        self.suppression_listeners.remove(suppression_listener)

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

    # read_datafeed function reads an array of events coming back from
    # DataFeedClient checks to see that sender's email is not equal to Bot's
    # email in config filemthis functionality helps bot avoid entering an
    # infinite loop where it responds to its own messageSent
    # after an event comes back over the dataFeed, the json object returned
    # from read_datafeed() gets passed to handle_event()
    def read_datafeed(self):

        while not self.stop:
            try:
                events = self.datafeed_client.read_datafeed(self.datafeed_id)
            except Exception as exc:
                self.handle_datafeed_errors(exc)
                continue
            
            self.decrease_timeout()
            if events:
                for event in events:
                    if self.log_events:
                        log.info(
                            'DataFeedEventService/read_datafeed() --> '
                            'Incoming event: {}'.
                            format(json.dumps(event, indent=4)))

                    else:
                        log.info(
                            'DataFeedEventService/read_datafeed() --> '
                            'Incoming event with id: {}'
                            .format(event['id'])
                        )

                    if event['initiator']['user']['userId'] != \
                            self.bot_client.get_bot_user_info()['id']:
                        self.handle_event(event)
            else:
                log.debug(
                    'DataFeedEventService() - no data coming in from '
                    'datafeed: {}'.format(self.datafeed_id)
                )

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

    def handle_datafeed_errors(self, thrown_exception):
        """Various errors may get thrown by the datafeed reader, from 500s when a server node is
        being bounced, intermittent connectivity or SSL problems. With the exception of a 403
        UnauthorisedError where reauthentication occurs upstream, these are all handled in
        the same way - sleep, request a new datafeed id and then retry.
        """
        try:
            raise thrown_exception
        except UnauthorizedException:
            log.error(
                'DataFeedEventService - caught unauthorized exception'
            )
        except (DatafeedExpiredException, APIClientErrorException, ServerErrorException) as exc:
            log.error(
                'DataFeedEventService - ' + str(exc)
            )
        except Exception as exc:
            log.exception(
                'DataFeedEventService - Unknown exception: ' + str(exc)
            )
        sleep_for = self.get_and_increase_timeout(thrown_exception)
        log.info('DataFeedEventService/handle_event() --> Sleeping for {:.4g}s'.format(sleep_for))
        time.sleep(sleep_for)
        try:
            log.info('DataFeedEventService/handle_event() --> Restarting Datafeed')
    
            self.datafeed_id = self.datafeed_client.create_datafeed()
      
        except Exception as exc:
            if str(exc) == 'max auth retry limit':
                raise
            else:
                self.handle_datafeed_errors(exc)

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
            log.debug('DataFeedEventService/get_and_increase_timeout --> '
                'Decreasing timeout from {:.4g}s to {:.4g}s'.format(original, new_timeout))
            self.current_timeout_sec = new_timeout
        return self.current_timeout_sec
        

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

    def demoted_to_owner(self, payload):
        log.debug('demoted_to_Owner')
        demoted_to_owner_data = payload['payload']['roomMemberDemotedFromOwner']
        for listener in self.room_listeners:
            listener.on_room_member_demoted_from_owner(demoted_to_owner_data)

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


# It might be possible to do this all in the same class, but that would require some trickery like:
# async def message_sent_handler(payload):
#     for listener in listeners:
#         handler = listener.on_im_message
#         if asyncio.iscoroutinefunction(handler):
#             await handler(payload):
#         else:
#             handler(payload)
#
# So for now this is a separate subclass with a lot of copy and pasted code
class AsyncDataFeedEventService(DataFeedEventService):
    """Non-blocking datafeed event service.

    The main advantage this carries over DataFeedEventService is that read_datafeed is non-blocking
    and therefore a bot can listen to this feed and conduct other activities at the same time. This
    is achieved with async / await. It would typically be used as following:

        datafeed_event_service = bot_client.get_async_datafeed_event_service()
        datafeed_event_service.add_im_listener(async_listener)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(datafeed_event_service.start_datafeed())
    
    There are several things to note about using this datafeed instead of the synchronous version:
        * All methods in the listener must be declared async def. Even if there is no async code
          inside them failing to declare them as such will likely cause an error when the service
          awaits them.
        * Listener methods that are expensive and not awaited will block reading the datafeed. For
          common IO-bound operations an asychronous version may be available, aiohttp instead of
          requests for example. If one is not, consider running it in a ThreadPoolExecutor
        * Some assumptions about ordering will fail. For example a user sending two messages to a
          bot in quick succession may get their responses in a different order.

    Potential improvements:
        * Provide a timeout to allow handlers to be cancelled after a certain period
        * Allow exception handling around listeners to be customised
    """


    def __init__(self, *args, **kwargs):
        self.queue = asyncio.Queue()
        self.exception_queue = asyncio.Queue()
        self.exception_handler = kwargs.pop('exception_handler', None)
        self.trace_enabled = kwargs.pop('trace_enabled', True)
        self.trace_recorder = kwargs.pop('trace_recorder', None)
        self.trace_dict = {}
        self.handle_events_task = None
        self.tasks = []
        super().__init__(*args, **kwargs)
    

    async def start_datafeed(self):
        log.info('AsyncDataFeedEventService/start_datafeed()')
        self.datafeed_id = self.datafeed_client.create_datafeed()
        await asyncio.gather(self.read_datafeed(), self.handle_events(), self.handle_exceptions())

    async def deactivate_datafeed(self, wait_for_handler_completions=True):
        """Deactivating the datafeed may take up to 30 seconds while waiting for
        a 204 from the read_datafeed API"""
        log.debug('AsyncDataFeedEventService/deactivate_datafeed()')
        if wait_for_handler_completions:
            log.info('AsyncDataFeedEventService/deactivate_datafeed() --> '
                         'Waiting for {} events to finish'.format(self.queue.qsize()))
            await self.queue.join()
            log.info('AsyncDataFeedEventService/deactivate_datafeed() --> '
                         'Deactivating')
        else:
            log.info('AsyncDataFeedEventService/deactivate_datafeed() --> '
                '{} events still being handled, deactivating anyway'.format(self.queue.qsize()))
        
        if not self.stop:
            self.stop = True
        await self.queue.put(None)
        await self.exception_queue.put(None)

    async def read_datafeed(self):
        while not self.stop:
            try:
                events = await self.datafeed_client.read_datafeed_async(self.datafeed_id)

            except Exception as exc:
                await self.handle_datafeed_errors(exc)
                continue
            
            self.decrease_timeout()
            if events:
                bot_id = self.bot_client.get_bot_user_info()['id']
                for event in events:
                    if self.log_events:
                        log.info(
                            'AsyncDataFeedEventService/read_datafeed() --> '
                            'Incoming data from read_datafeed(): {}'
                            .format(json.dumps(event['payload'], indent=4))
                        )
                    else:
                        log.info(
                            'AsyncDataFeedEventService/read_datafeed() --> '
                            'Incoming event from read_datafeed() with id: {}'.format(event['id'])   
                        )
                    if event['initiator']['user']['userId'] != bot_id:
                        e_id = event["messageId"] if "messageId" in event else event["id"]
                        self._add_trace(e_id, event["timestamp"])
                        await self.queue.put(event)
                    log.debug(f"Event queued. Current queue size: {self.queue.qsize()}")

            else:
                log.debug(
                    'DataFeedEventService() - no data coming in from '
                    'datafeed: {}'.format(self.datafeed_id)
                )

    async def handle_datafeed_errors(self, thrown_exception):
        """Various errors may get thrown by the datafeed reader, from 500s when a server node is
        being bounced, intermittent connectivity or SSL problems. With the exception of a 403
        UnauthorisedError where reauthentication occurs upstream, these are all handled in
        the same way - sleep, request a new datafeed id and then retry.
        """
        try:
            raise thrown_exception
        except UnauthorizedException:
            log.error(
                'AsyncDataFeedEventService - caught unauthorized exception'
            )
        except (DatafeedExpiredException, APIClientErrorException, ServerErrorException) as exc:
            log.error(
                'AsyncDataFeedEventService - ' + str(exc)
            )
        except Exception as exc:
            log.exception(
                'AsyncDataFeedEventService - Unknown exception: ' + str(exc)
            )

        sleep_for = self.get_and_increase_timeout(thrown_exception)
        log.info('AsyncDataFeedEventService/handle_event() --> Sleeping for {:.4g}s'.format(sleep_for))
        await asyncio.sleep(sleep_for)
        try:
            log.info('AsyncDataFeedEventService/handle_event() --> Restarting Datafeed')
    
            self.datafeed_id = self.datafeed_client.create_datafeed()
        except Exception as exc:
            if str(exc) == 'max auth retry limit':
                raise
            else:
                self.handle_datafeed_errors(exc)

    def _check_result(self, e_id, task):
        """Callback for task completion. If exceptions occurred add them for processing on the
        exceptions queue, otherwise they get swallowed by the future
        """
        self._add_trace(e_id)
        if task.exception() is not None:
            log.debug("Adding exception to exception queue for event: {}".format(e_id))
            self.exception_queue.put_nowait((e_id, task))
        else:
            self._process_full_trace(e_id)
        self.queue.task_done()

    def _process_full_trace(self, id):
        """Process all tracedata for the current request and append it to trace_recorder, if defined.

        Use with messagedId if available        
        """

        if self.trace_enabled:
            try:
                intermediates = self.trace_dict[id]
                assert len(intermediates) == 4
                trace = EventTrace(id, intermediates[0], intermediates[1], intermediates[2], 
                                intermediates[3])
                total_time = intermediates[3] - intermediates[0]
                time_in_bot = intermediates[3] - intermediates[1]

                # This just writes out total seconds instead of formatting into minutes and hours
                # for a typical bot response this seems reasonable
                log.info("Responded to message in: {:.4g}s. Including {:.4g}s inside the bot"
                            .format(total_time.total_seconds(), time_in_bot.total_seconds()))
                if self.trace_recorder is not None:
                    trace_recorder.append(trace)
                del self.trace_dict[id]
            except Exception as exc:
                log.error("Error while computing trace results for id: " + id)
                log.exception(exc)

    def _add_trace(self, e_id, first_timestamp=None):
        """Take the current timestamp and add if to the trace_dict, used to trace the time taken
        to process events.
        
        Use with messageId if available
        """
        if self.trace_enabled:
            if first_timestamp is not None:
                self.trace_dict[e_id] = [make_datetime(first_timestamp)]
            try:
                self.trace_dict[e_id].append(datetime.datetime.utcnow())
            except KeyError:
                log.error(
                    'Error making traces for {}. Has the same messageId appeared'
                    'more than once?'.format(e_id)
                )

    async def handle_events(self):
        """For each event resolve its handler and add it to the queue to be processed"""
        while not self.stop:
            event = await self.queue.get()

            if event is None:
                # None is a sentinel to indicate the that work is done and there will be no more
                # messages. If there are multiple consumers of the queue, this will become an
                # issue as None will need to be added for each consumer
                self.queue.task_done()
            else:
                event_type = str(event['type'])
                e_id = event["messageId"] if "messageId" in event else event["id"]
                self._add_trace(e_id)

                log.debug('AsyncDataFeedEventService/handle_events() --> event-type:' + event_type)
                try:
                    route = self.routing_dict[event_type]
                except KeyError:
                    log.debug('no event detected')
                    self.queue.task_done()
                    return
                
                future = asyncio.ensure_future(route(event))
                future.add_done_callback(partial(self._check_result, e_id))
    
    async def handle_exceptions(self):
        """If exceptions are not excplicitly handled they'll silently fail in the co-routine.
        This method picks results one by one off the queue and checks if they were successful, using
        the provided exception handler or failing otherwise"""
        while not self.stop:
            log.debug("Waiting on new exception, queue size: {}".format(self.exception_queue.qsize()))
            exception_event = await self.exception_queue.get()
            if exception_event is None:
                # Same as handle_events, None is a sentinel to close the queue and finish
                self.exception_queue.task_done()
            else:
                e_id, fut = exception_event
                try:
                    await fut
                except Exception as exc:
                    if self.exception_handler is not None:
                        self.exception_handler(exc)
                    else:
                        raise exc

                self._add_trace(e_id)
                self._process_full_trace(e_id)
                self.exception_queue.task_done()          

    async def msg_sent_handler(self, payload):
        """This handler is used for both room messages and IMs. Which listener is invoked
        depends on the streamType"""
        log.debug('async msg_sent_handler function started')
        stream_type = payload['payload']['messageSent']['message']['stream']['streamType']
        message_sent_data = payload['payload']['messageSent']['message']
        if str(stream_type) == 'ROOM':
            for listener in self.room_listeners:
                await listener.on_room_msg(message_sent_data)
        else:
            for listener in self.im_listeners:
                await listener.on_im_message(message_sent_data)

    async def instant_msg_handler(self, payload):
        log.debug('async instant_msg_handler function started')
        instant_message_data = payload['payload']['instantMessageCreated']
        for listener in self.im_listeners:
            await listener.on_im_created(instant_message_data)

    async def room_created_handler(self, payload):
        log.debug('async room_created_handler function started')
        room_created_data = payload['payload']['roomCreated']
        for listener in self.room_listeners:
            await listener.on_room_created(room_created_data)

    async def room_updated_handler(self, payload):
        log.debug('async room_updated_handler')
        room_updated_data = payload['payload']['roomUpdated']
        for listener in self.room_listeners:
            await listener.on_room_updated(room_updated_data)

    async def room_deactivated_handler(self, payload):
        log.debug('async room_deactivated_handler')
        room_deactivated_data = payload['payload']['roomDeactivated']
        for listener in self.room_listeners:
            await listener.on_room_deactivated(room_deactivated_data)

    async def room_reactivated_handler(self, payload):
        log.debug('async room_reactivated_handler')
        room_reactivated_data = payload['payload']['roomReactivated']
        for listener in self.room_listeners:
            await listener.on_room_reactivated(room_reactivated_data)

    async def user_joined_room_handler(self, payload):
        log.debug('async user_joined_room_handler')
        user_joined_room_data = payload['payload']['userJoinedRoom']
        for listener in self.room_listeners:
            await listener.on_user_joined_room(user_joined_room_data)

    async def user_left_room_handler(self, payload):
        log.debug('async user_left_room_handler')
        user_left_room_data = payload['payload']['userLeftRoom']
        for listener in self.room_listeners:
            await listener.on_user_left_room(user_left_room_data)

    async def promoted_to_owner(self, payload):
        log.debug('async promoted_to_owner')
        promoted_to_owner_data = payload['payload']['roomMemberPromotedToOwner']
        for listener in self.room_listeners:
            await listener.on_room_member_promoted_to_owner(promoted_to_owner_data)

    async def demoted_to_owner(self, payload):
        log.debug('async demoted_to_Owner')
        demoted_to_owner_data = payload['payload']['roomMemberDemotedFromOwner']
        for listener in self.room_listeners:
            await listener.on_room_member_demoted_from_owner(demoted_to_owner_data)

    async def shared_post_handler(self, payload):
        log.debug('shared_post_handler')
        shared_post = payload['payload']['sharedPost']
        for listener in self.wall_post_listeners:
            await listener.on_shared_post(shared_post)
    
    async def suppressed_message_handler(self, payload):
        log.debug('suppressed_message_handler')
        message_suppressed = payload['payload']['messageSuppressed']
        for listener in self.suppression_listeners:
            await listener.on_message_suppression(message_suppressed)

