import asyncio
import uuid
from functools import partial
import logging
import datetime
from collections import namedtuple

from asyncio import CancelledError

# TODO: These imports are duplicated over the abstract class to avoid errors in the Async version
from .exceptions.UnauthorizedException import UnauthorizedException
from .exceptions.APIClientErrorException import APIClientErrorException
from .exceptions.DatafeedExpiredException import DatafeedExpiredException
from .exceptions.ServerErrorException import ServerErrorException
from .exceptions.MaxRetryException import MaxRetryException

from .services.abstract_datafeed_event_service import AbstractDatafeedEventService
from .clients.constants.DatafeedVersion import DatafeedVersion
from .services.datafeed_event_service_v1 import DataFeedEventServiceV1
from .services.datafeed_event_service_v2 import DataFeedEventServiceV2

log = logging.getLogger(__name__)


def make_datetime(unix_timestamp_millis):
    seconds, millis = divmod(unix_timestamp_millis, 1000)
    return datetime.datetime.utcfromtimestamp(seconds).replace(microsecond=millis * 1000)


EventTrace = namedtuple('EventTrace', 'message_id creation_time bot_received listeners_complete bot_complete')


class DataFeedEventService:

    def __init__(self, sym_bot_client, error_timeout_sec=None, maximum_timeout_sec=None):
        config = sym_bot_client.get_sym_config()

        # Creating the DataFeed Event Service
        if DatafeedVersion.version_of(config.data.get("datafeedVersion")) == DatafeedVersion.V2:
            self.datafeed_event_service = DataFeedEventServiceV2(sym_bot_client, error_timeout_sec=error_timeout_sec,
                                                                 maximum_timeout_sec=maximum_timeout_sec)
        else:
            self.datafeed_event_service = DataFeedEventServiceV1(sym_bot_client, error_timeout_sec=error_timeout_sec,
                                                                 maximum_timeout_sec=maximum_timeout_sec)

    def start_datafeed(self):
        """Start reading events from datafeed.
        """
        self.datafeed_event_service.start_datafeed()

    def read_datafeed(self):
        self.datafeed_event_service.read_datafeed()

    def activate_datafeed(self):
        self.datafeed_event_service.activate_datafeed()

    def deactivate_datafeed(self):
        self.datafeed_event_service.deactivate_datafeed()

    def add_room_listener(self, room_listener):
        self.datafeed_event_service.add_room_listener(room_listener)

    def remove_room_listener(self, room_listener):
        self.datafeed_event_service.remove_room_listener(room_listener)

    def add_im_listener(self, im_listener):
        self.datafeed_event_service.add_im_listener(im_listener)

    def remove_im_listener(self, im_listener):
        self.datafeed_event_service.remove_im_listener(im_listener)

    def add_elements_listener(self, elements_listener):
        self.datafeed_event_service.add_elements_listener(elements_listener)

    def remove_elements_listener(self, elements_listener):
        self.datafeed_event_service.remove_elements_listener(elements_listener)

    def add_connection_listener(self, connection_listener):
        self.datafeed_event_service.add_connection_listener(connection_listener)

    def remove_connection_listener(self, connection_listener):
        self.datafeed_event_service.remove_connection_listener(connection_listener)

    def add_wall_post_listener(self, wall_post_listener):
        self.datafeed_event_service.add_wall_post_listener(wall_post_listener)

    def remove_wall_post_listener(self, wall_post_listener):
        self.datafeed_event_service.remove_wall_post_listener(wall_post_listener)

    def add_suppression_listener(self, suppression_listener):
        self.datafeed_event_service.add_suppression_listener(suppression_listener)

    def remove_suppression_listener(self, suppression_listener):
        self.datafeed_event_service.remove_suppression_listener(suppression_listener)

    def handle_events(self, events):
        self.datafeed_event_service.handle_events(events)

    def handle_event(self, payload):
        self.datafeed_event_service.handle_event(payload)

    ### Handlers ###
    def msg_sent_handler(self, payload):
        self.datafeed_event_service.msg_sent_handler(payload)

    def instant_msg_handler(self, payload):
        self.datafeed_event_service.instant_msg_handler(payload)

    def room_created_handler(self, payload):
        self.datafeed_event_service.room_created_handler(payload)

    def room_updated_handler(self, payload):
        self.datafeed_event_service.room_updated_handler(payload)

    def room_deactivated_handler(self, payload):
        self.datafeed_event_service.room_deactivated_handler(payload)

    def room_reactivated_handler(self, payload):
        self.datafeed_event_service.room_reactivated_handler(payload)

    def user_joined_room_handler(self, payload):
        self.datafeed_event_service.user_joined_room_handler(payload)

    def user_left_room_handler(self, payload):
        self.datafeed_event_service.user_left_room_handler(payload)

    def promoted_to_owner(self, payload):
        self.datafeed_event_service.promoted_to_owner(payload)

    def demoted_from_owner(self, payload):
        self.datafeed_event_service.demoted_from_owner(payload)

    def connection_accepted_handler(self, payload):
        self.datafeed_event_service.connection_accepted_handler(payload)

    def connection_requested_handler(self, payload):
        self.datafeed_event_service.connection_requested_handler(payload)

    def elements_action_handler(self, payload):
        self.datafeed_event_service.elements_action_handler(payload)

    def shared_post_handler(self, payload):
        self.datafeed_event_service.shared_post_handler(payload)

    def suppressed_message_handler(self, payload):
        self.datafeed_event_service.suppressed_message_handler(payload)

    ### Handle errors ###
    def get_and_increase_timeout(self, previous_exc=None):
        self.datafeed_event_service.get_and_increase_timeout(previous_exc)

    def decrease_timeout(self):
        self.datafeed_event_service.decrease_timeout()


class AsyncDataFeedEventService(AbstractDatafeedEventService):
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

    Known Issues:
        On Windows with Python 3.8+ there is a known issue with aiohttp and setting a proxy
        that can be found at https://github.com/aio-libs/aiohttp/issues/4536

        To work around this we must specify the event loop to use WindowsSelectorEventLoopPolicy with:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        If cross-platform code is needed you can use a check:
        if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = asyncio.Queue()
        self.exception_queue = asyncio.Queue()
        self.exception_handler = kwargs.pop('exception_handler', None)
        self.trace_enabled = kwargs.pop('trace_enabled', True)
        self.trace_recorder = kwargs.pop('trace_recorder', None)
        self.trace_dict = {}
        self.handle_events_task = None
        self.tasks = []
        self.datafeed_id = None

    async def start_datafeed(self):
        log.debug('AsyncDataFeedEventService/start_datafeed()')
        self.datafeed_id = self._get_from_file_or_create_datafeed_id()
        await asyncio.gather(self.read_datafeed(), self.handle_events(), self.handle_exceptions())

    async def deactivate_datafeed(self, wait_for_handler_completions=True):
        """Deactivating the datafeed may take up to 30 seconds while waiting for
        a 204 from the read_datafeed API"""
        log.debug('AsyncDataFeedEventService/deactivate_datafeed()')
        if wait_for_handler_completions:
            log.debug('AsyncDataFeedEventService/deactivate_datafeed() --> '
                      'Waiting for {} events to finish'.format(self.queue.qsize()))
            await self.queue.join()
            log.debug('AsyncDataFeedEventService/deactivate_datafeed() --> '
                      'Deactivating')
        else:
            log.debug('AsyncDataFeedEventService/deactivate_datafeed() --> '
                      '{} events still being handled, deactivating anyway'.format(self.queue.qsize()))

        if not self.stop:
            self.stop = True

        await self.queue.put(None)
        await self.exception_queue.put(None)
        await self.bot_client.close_async_sessions()

    async def read_datafeed(self):
        while not self.stop:
            try:
                events = await self.datafeed_client.read_datafeed_async(self.datafeed_id)
            except CancelledError as exc:
                log.info("Cancel request received. Stopping datafeed...")
                await self.deactivate_datafeed()
                raise
            except Exception as exc:
                try:
                    await self.handle_datafeed_errors(exc)
                except Exception as inner_exc:
                    await self.deactivate_datafeed(wait_for_handler_completions=False)
                    raise inner_exc from None
                continue

            self.decrease_timeout()
            if events:
                bot_id = self.bot_client.get_bot_user_info()['id']
                for event in events:
                    log.debug(
                        'AsyncDataFeedEventService/read_datafeed() --> '
                        'Incoming event from read_datafeed() with id: {}'.format(event.get('id'))
                    )

                    if event['initiator']['user']['userId'] != bot_id:
                        e_id = self._get_event_id(event)
                        self._add_trace(e_id, event["timestamp"])
                        await self.queue.put(event)
                    log.debug(f"Event queued. Current queue size: {self.queue.qsize()}")

            else:
                log.debug(
                    'AsyncDataFeedEventService() - no data coming in from '
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
            log.error('AsyncDataFeedEventService - caught unauthorized exception')
        except MaxRetryException as exc:
            log.error('AsyncDataFeedEventService - Bot has failed to authenticate more than 5 times ')
            raise exc from None

        except (DatafeedExpiredException, APIClientErrorException, ServerErrorException) as exc:
            log.error('AsyncDataFeedEventService - ' + str(exc))

        except Exception as exc:
            log.exception('AsyncDataFeedEventService - Unknown exception: ' + str(exc))

        sleep_for = self.get_and_increase_timeout(thrown_exception)
        log.debug('AsyncDataFeedEventService/handle_event() --> Sleeping for {:.4g}s'.format(sleep_for))
        await asyncio.sleep(sleep_for)
        try:
            log.debug('AsyncDataFeedEventService/handle_event() --> Restarting Datafeed')
            self.datafeed_id = self._create_datafeed_and_persist()
        except Exception as exc:
            await self.handle_datafeed_errors(exc)

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

        if not self.trace_enabled:
            return

        try:
            intermediates = self.trace_dict[id]
            if len(intermediates) != 4:
                log.error("Error while computing trace results for id: " + id + ": trace item should have 4 elements")
                return

            trace = EventTrace(id, intermediates[0], intermediates[1], intermediates[2],
                               intermediates[3])
            total_time = intermediates[3] - intermediates[0]
            time_in_bot = intermediates[3] - intermediates[1]

            # This just writes out total seconds instead of formatting into minutes and hours
            # for a typical bot response this seems reasonable
            log.debug("Responded to message in: {:.4g}s. Including {:.4g}s inside the bot"
                      .format(total_time.total_seconds(), time_in_bot.total_seconds()))
            if self.trace_recorder is not None:
                self.trace_recorder.append(trace)
            del self.trace_dict[id]
        except Exception as exc:
            log.error("Error while computing trace results for id: " + id)
            log.exception(exc)

    @staticmethod
    def _get_event_id(event):
        event_id = event["messageId"] if "messageId" in event else event.get('id')
        if event_id is None:
            event['id'] = str(uuid.uuid4())
            return event['id']
        return event_id

    def _add_trace(self, e_id, first_timestamp=None):
        """Take the current timestamp and add if to the trace_dict, used to trace the time taken
        to process events.

        Use with messageId if available
        """
        if not self.trace_enabled:
            return

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
                e_id = self._get_event_id(event)
                self._add_trace(e_id)

                log.debug('AsyncDataFeedEventService/handle_events() --> event-type:' + event_type)
                try:
                    route = self.routing_dict[event_type]
                except KeyError:
                    log.debug('Event with unsupported type ' + event_type + ' detected')
                    self.queue.task_done()
                    continue

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

    async def demoted_from_owner(self, payload):
        log.debug('async demoted_from_owner')
        demoted_to_owner_data = payload['payload']['roomMemberDemotedFromOwner']
        for listener in self.room_listeners:
            await listener.on_room_member_demoted_from_owner(demoted_to_owner_data)

    async def connection_accepted_handler(self, payload):
        log.debug('async connection_accepted_handler')
        connection_accepted_data = payload['payload']['connectionAccepted']
        for listener in self.connection_listeners:
            await listener.on_connection_accepted(connection_accepted_data)

    async def connection_requested_handler(self, payload):
        log.debug('async connection_requested_handler')
        connection_requested_data = payload['payload']['connectionRequested']
        for listener in self.connection_listeners:
            await listener.on_connection_requested(connection_requested_data)

    async def elements_action_handler(self, payload):
        log.debug('async elements_action_handler')
        for listener in self.elements_listeners:
            await listener.on_elements_action(payload)

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
