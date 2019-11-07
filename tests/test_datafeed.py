"""Testing the datafeed in various forms

The decision was taken not to fully mock out the datafeed due to the complexity of doing so,
however the events can be simulated.

Some of this content could potentially be in the src directories, such that downstream
projects can use this framework to do event testing of their own.

Unfortunately it wasn't possible to use one mocking library to test both synchronous and
asychronous reads. The only library claiming to be able to do so at the unittest level
(rather than vcrpy) was Mocket - proudly claiming to be like other mocking libraries
but without regex path matching and dynamic responses. Unfortunately these are two needed
features. requests-mock and aioresponses have therefore been chosen.
"""

import asyncio
import copy
from itertools import count
import logging
import re
import unittest
from unittest.mock import patch
import uuid

import requests_mock
from aioresponses import aioresponses, CallbackResult

from sym_api_client_python.loaders import load_from_env_var
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.datafeed_event_service import DataFeedEventService, AsyncDataFeedEventService
from sym_api_client_python.clients.datafeed_client import DataFeedClient
from sym_api_client_python.listeners.im_listener import IMListener
from sym_api_client_python.exceptions.DatafeedExpiredException import DatafeedExpiredException

_STOP_EVENT = 'TEST_STOP_EVENT'
_CREATE_DATAFEED_URL = '/agent/v4/datafeed/create'
_READ_DATAFEED_URL = re.compile('^.*/agent/v4/datafeed/.*/read')
_SESSION_INFO = '/pod/v2/sessioninfo'

_EVENT = {
    "id": "ulPr8a:eFFDL7",
    "messageId": "1234",
    "timestamp": 1536346282592,
    "type": "MESSAGESENT",
    "initiator": {
        "user": {
            "userId": "1456852...",
            "displayName": "Local Bot01",
            "email": "bot.user1@test.com",
            "username": "bot.user1"
        }
    },
    "payload": {
        "messageSent": {
            "message": {
                "messageId": "CszQa6uPAA9...",
                "timestamp": 1536346282592,
                "message": "<div data-format=\"PresentationML\" data-version=\"2.0\">Hello World</div>",
                "data": "{\"entityIdentifier\":{\"type\":\"org.symphonyoss.fin.security\",\"version\":\"0.1\",\"id\":[{\"type\":\"org.symphonyoss.fin.security.id.isin\",\"value\":\"US0378\"},{\"type\":\"org.symphonyoss.fin.security.id.cusip\",\"value\":\"037\"},{\"type\":\"org.symphonyoss.fin.security.id.openfigi\",\"value\":\"BBG000\"}]}}",
                "user": {
                    "userId": "14568529...",
                    "displayName": "Local Bot01",
                    "email": "bot.user1@ntest.com",
                    "username": "bot.user1"
                },
                "stream": {
                    "streamId": "wTmSDJSNPXgB...",
                    "streamType": "IM"
                },
                "externalRecipients": False,
                "userAgent": "Agent-2.2.8-Linux-4.9.77-31.58.amzn1.x86_64",
                "originalFormat": "com.symphony.messageml.v2"
            }
        }
    }
}

class SymphonyApiMocker:
    """Mocker to wrap requests_mock and aioresponses in one

    For testing the synchronous datafeed, only requests_mock is needed. However for testing the
    async datafeed both are needed as requests_mock handles the mocking for the methods that 
    don't have an async counterpart like create_datafeed().

    Pass aio=True to mock through to the asynchronous datafeed, which uses aiohttp for REST
    requests and aioresponses for the mocking
    """
    def __init__(self, aio=False):
        self.requests_mock_manager = requests_mock.Mocker()
        if aio:
            self.aioresponses_manager = aioresponses()
        self.aio = aio
    
    def __enter__(self):
        """This function just makes sure various core URLs like the create and session datafeed
        examples are allowed to make real http requests. Without this NoMockFound errors will be
        thrown when non-mocked errors are accessed."""
        self.requests_mock_manager.register_uri(
            'POST', _CREATE_DATAFEED_URL, status_code=200, json=self.dummy_id_provider()
            )
        self.requests_mock_manager.register_uri('GET', _SESSION_INFO, real_http=True)
        self.requests_mock_manager.__enter__()
        if self.aio:
            self.aioresponses_manager.__enter__()
        return self
    
    def __exit__(self, *args):
        self.requests_mock_manager.__exit__(*args)

        if self.aio:
            self.aioresponses_manager.__exit__(*args)

    def add_mock_events(self, events_list, add_stop_event=True):

        if self.aio:
            # Mock for aioreponses
            for events in events_list:
                self.aioresponses_manager.get(_READ_DATAFEED_URL, **events)

            if add_stop_event:
                self.aioresponses_manager.get(
                    _READ_DATAFEED_URL, **make_events([_STOP_EVENT], aio=True)
                )
                self.aioresponses_manager.get(
                    _READ_DATAFEED_URL, callback=make_timed_callback(5), repeat=True
                )
        else:
            if add_stop_event:
                events_list.append(make_events([_STOP_EVENT]))
            
            self.requests_mock_manager.register_uri('GET', _READ_DATAFEED_URL, events_list)

    def dummy_id_provider(self):
        counter = count(1)
        def f(*args, _counter=counter, **kwargs):
            feed_response = {
                "id": "DUMMY-DATAFEED-ID-{}".format(next(_counter))
            }
            return feed_response
        return f


def make_events(event_types=None, count=None, messages=None, aio=False):
    """Returns a dict to be consumed by a requests-mock object, specifically for the
    read_datafeed API.
        event = make_event()
        m.register_uri('GET', SOME_URL, **event)
    """
    events = []
    if event_types is None:
        count = 1 if count is None else count
        event_types = [None for _ in range(count)]
    else:
        if count is not None and len(event_types) != count:
            raise ValueError("Mismatching length")
    
    if messages is None:
        messages = [None for _ in event_types]
        
    for event_type, message in zip(event_types, messages):
        event = copy.deepcopy(_EVENT)

        # Generate unique event and message ids
        event["id"] = "EVENT-" + str(uuid.uuid4())
        message_id = "MESSAGE-" + str(uuid.uuid4())
        if "messageId" in event:
            event["messageId"] = message_id
        
        if "messageId" in event["payload"]["messageSent"]["message"]:
            event["payload"]["messageSent"]["message"]["messageId"] = message_id
        else:
            logging.error(event["payload"]["messageSent"]["message"].keys())
        if event_type is not None:
            event['type'] = event_type
        if message is not None:
            original = event["payload"]["messageSent"]["message"]["message"]
            modified = original.replace("Hello World", message)
            event["payload"]["messageSent"]["message"]["message"] = modified
        events.append(event)

    # Different mockers take kwargs in different forms
    if aio:
        return {"payload": events, "status": 200}
    else:
        return {"json": events, "status_code": 200}

def make_error(status_code, error_message=None, aio=False):
    """Returns an error as a dict to be consumed by a requests-mock like:
        error = make_error()
        m.register_uri('GET', SOME_URL, **error)
    """
    if error_message is None:
        # Replace with the generic Symphony error message
        error_message = "An error occurred"

    json_body = {"code": status_code, "message": error_message}
    
    if aio:
        return {"payload": json_body, "status": status_code}
    else:
        return {"json": json_body, "status_code": status_code}


class StoppableService(DataFeedEventService):
    """The synchronous datafeed blocks on read, meaning anything that tests it will run forever.
    This custom version allows for passing in a STOP event to cancel reading, and end the test.
    All tests that are expected to end without exception should pass a final stop event.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.baseline_timeout_sec = 2
        self.current_timeout_sec = 2
        self.lower_threshold = 2

        if _STOP_EVENT not in self.routing_dict:
            self.routing_dict[_STOP_EVENT] = self._stop_feed_handler

    def _stop_feed_handler(self, payload):
        self.deactivate_datafeed()

class TestDataFeed(unittest.TestCase):

    # Unlike setUp this only fires once per class
    @classmethod
    def setUpClass(cls):
        logging.debug('testing synchronous datafeed')
        try:
            conf, auth = load_from_env_var("SYMPHONY_TEST_CONFIG")
            cls.configure = conf
            cls.auth = auth
        except ValueError:
            #RSA Auth flow:
            cls.configure = SymConfig('sym_api_client_python/resources/hackathon_config.json')
            cls.configure.load_config()
            cls.auth = SymBotRSAAuth(cls.configure)
            cls.auth.authenticate()

        # Initialize SymBotClient with auth and configure objects
        cls.bot_client = SymBotClient(cls.auth, cls.configure)
    
    def test_start_datafeed_and_stop(self):
        """Test the stop event works for the custom datafeed"""
        with SymphonyApiMocker() as m:
            m.add_mock_events([])

            event_service = StoppableService(self.bot_client)
            event_service.start_datafeed()

    def test_start_datafeed_and_stop_multiple_messages(self):
        """Test the stop event works for the custom datafeed when multiple events are
        passed at once"""
        with SymphonyApiMocker() as m:
            m.add_mock_events([make_events(count=2), make_events([None, None, _STOP_EVENT])],
                add_stop_event=False
            )

            event_service = StoppableService(self.bot_client)
            event_service.start_datafeed()

            datafeed_calls = [
                req for req in m.requests_mock_manager.request_history
                if _READ_DATAFEED_URL.match(req.url)
                ]

            self.assertEqual(len(datafeed_calls), 2)

    def test_datafeed_server_500(self):
        """Ideally the retry logic would be tested for more complicated situations like multiple
        consecutive 500 errors, but global timeouts, and constantly reauthenticating during the
        test suite makes this difficult to do in isolation"""

        with SymphonyApiMocker() as m:

            events = [make_events(count=2), make_error(503), make_events(count=2)]

            m.add_mock_events(events)

            event_service = StoppableService(self.bot_client)
            event_service.start_datafeed()
    
    def test_datafeed_doesnt_exist_400(self):
        """This is a fairly common occurence in the wild"""

        with SymphonyApiMocker() as m:
            events = [
                make_events(count=2),
                make_error(400,
                "Could not find a datafeed with the id: XXXXX"),
                make_events(count=2)
            ]

            m.add_mock_events(events)

            event_service = StoppableService(self.bot_client, log_events=True)
            event_service.start_datafeed()
    
    def test_datafeed_throws_after_enough_exceptions(self):
        
        events = [
            make_events(count=2),
            make_error(400,
            "Could not find a datafeed with the id: XXXXX"),
            make_error(400,
            "Could not find a datafeed with the id: XXXXX"),
            make_error(400,
            "Could not find a datafeed with the id: XXXXX"),
            make_error(400,
            "Could not find a datafeed with the id: XXXXX"),
            make_error(400,
            "Could not find a datafeed with the id: XXXXX"),
        ]

        event_service = StoppableService(self.bot_client, log_events=True)
        event_service.baseline_timeout_sec = 0.1
        event_service.current_timeout_sec = 0.1
        event_service.lower_threshold = 0.1
        event_service.timeout_multiplier = 2.0
        event_service.upper_threshold = 1.0


        with SymphonyApiMocker() as m:

            m.add_mock_events(events)
            with self.assertRaises(RuntimeError, msg="threshold exceeded"):
                event_service.start_datafeed()
    
# Asynchronous Tests

class StoppableAsyncService(AsyncDataFeedEventService):
    """While other strategies could be employed to stop the async services, it's simpler for the
    purposes of these tests to keep the sync model.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if _STOP_EVENT not in self.routing_dict:
            self.routing_dict[_STOP_EVENT] = self._stop_feed_handler

    async def _stop_feed_handler(self, payload):
        asyncio.ensure_future(self.deactivate_datafeed())
    

def _run(coro):
    res = asyncio.get_event_loop().run_until_complete(coro)
    return res

def make_timed_callback(sleep_time=1):
    """Simulate the behaviour of the server, blocking for 30s and return a 204. Instead
    of waiting 30s by default it just waits 1"""

    async def timed_callback(url, **kwargs):
        await asyncio.sleep(sleep_time)
        return CallbackResult(status=204)

    return timed_callback

class TestAsyncDataFeed(unittest.TestCase):
    """The testing strategy for this class is taken from this post:
        https://blog.miguelgrinberg.com/post/unit-testing-asyncio-code

    Note that since there are only a few asychronous methods in the codebase for the
    moment, the create datafeed methods don't need separate aiohttp mocking, they
    will just use what's in place for requests
    """

    # Unlike setUp this only fires once per class
    @classmethod
    def setUpClass(cls):
        logging.debug('testing async datafeed class')
        try:
            conf, auth = load_from_env_var("SYMPHONY_TEST_CONFIG")
            cls.configure = conf
            cls.auth = auth
        except ValueError:
            #RSA Auth flow:
            cls.configure = SymConfig('sym_api_client_python/resources/hackathon_config.json')
            cls.configure.load_config()
            cls.auth = SymBotRSAAuth(cls.configure)
            cls.auth.authenticate()

        # Initialize SymBotClient with auth and configure objects
        cls.bot_client = SymBotClient(cls.auth, cls.configure)

    def test_start_datafeed_and_stop(self):
        """Test the stop event works for the custom datafeed"""

        with SymphonyApiMocker(True) as m:

            m.add_mock_events([make_events([_STOP_EVENT], aio=True)])

            event_service = StoppableAsyncService(self.bot_client)
            _run(event_service.start_datafeed())

    def test_datafeed_listeners_throw_errors(self):
        """Specific test to make sure errors thrown by listeners are not silently swallowed"""

        class ThrowingListener(IMListener):

            async def on_im_message(self, message):
                1/0

            async def on_im_created(self, stream):
                pass

        event_service = StoppableAsyncService(self.bot_client)
        event_service.add_im_listener(ThrowingListener())

        events = [make_events(count=1, aio=True)]

        with SymphonyApiMocker(True) as m:
            m.add_mock_events(events)
            with self.assertRaises(ZeroDivisionError):
                _run(event_service.start_datafeed())

    def test_datafeed_listeners_run_asynchronously(self):
        """Specific test to make sure messages are handled asynchronously. A slow handler
        and a fast handler are created, with a message going to the slow handler first.
        It's asserted that the fast handler returns first - meaning it wasn't blocked"""

        class SlowFastListener(IMListener):

            def __init__(self):
                self.count = 0
                self.completed = []

            async def on_im_message(self, message):
                current_count = self.count
                self.count += 1
                if current_count == 0:
                    await asyncio.sleep(1)
                
                self.completed.append(current_count)

    
            async def on_im_created(self, stream):
                pass

        event_service = StoppableAsyncService(self.bot_client)
        listener = SlowFastListener()
        event_service.add_im_listener(listener)

        # First batch of two messages SENTMESSAGE in one call
        first_batch = make_events(count=2, aio=True)
        # A second batch of two messages, 2nd, 3rd and 4th should complete before the 1st
        second_batch = make_events(count=2, aio=True)
        events = [first_batch, second_batch]

        with SymphonyApiMocker(True) as m:

            m.add_mock_events(events)
            _run(event_service.start_datafeed())


        # Doesn't matter what order the last three occurred, as long as they all
        # completed before the first one
        self.assertEqual(len(listener.completed), 4)
        self.assertEqual(listener.completed[-1], 0)



    def test_multiple_messages_in_array(self):
        """Specific test to make sure different messages delivered together are both
        recognised"""

        class RecordingListener(IMListener):

            def __init__(self):
                self.received = []

            async def on_im_message(self, message):
                logging.debug(message)                
                self.received.append(message["message"])
    
            async def on_im_created(self, stream):
                pass

        listener = RecordingListener()
        event_service = StoppableAsyncService(self.bot_client)
        event_service.add_im_listener(listener)

        expected_messages = ["Hello", "World"]
        # One message with Hello, another with World
        made_events = make_events(count=2, messages=expected_messages, aio=True)

        with SymphonyApiMocker(True) as m:

            m.add_mock_events([made_events])
            
            _run(event_service.start_datafeed())

        self.assertEqual(len(listener.received), 2)
        for expected in expected_messages:
            found = False
            for actual_message in listener.received:
                if expected in actual_message:
                    found = True
                    break
            self.assertTrue(found, "Did not find {} in {}".format(expected, listener.received))
            
    def test_async_datafeed_handles_400(self):

        events = [
            make_events(count=2, aio=True),
            make_error(400, "Could not find a datafeed with the id: XXXXX", aio=True),
            make_events(count=2, aio=True)
        ]
        event_service = StoppableAsyncService(self.bot_client)
        with SymphonyApiMocker(True) as m:

            m.add_mock_events(events)
            _run(event_service.start_datafeed())

    def test_async_datafeed_handles_500(self):

        events = [
            make_events(count=2, aio=True),
            make_error(503, "Server encountered an unknown error", aio=True),
            make_events(count=2, aio=True)
        ]
        event_service = StoppableAsyncService(self.bot_client)
        with SymphonyApiMocker(True) as m:

            m.add_mock_events(events)
            _run(event_service.start_datafeed())

    def test_async_datafeed_eventually_throws(self):

        events = [
            make_events(count=2, aio=True),
            make_error(400,"Could not find a datafeed with the id: XXXXX", aio=True),
            make_error(400,"Could not find a datafeed with the id: XXXXX", aio=True),
            make_error(400,"Could not find a datafeed with the id: XXXXX", aio=True),
            make_error(400,"Could not find a datafeed with the id: XXXXX", aio=True),
            make_error(400,"Could not find a datafeed with the id: XXXXX", aio=True),
        ]

        event_service = StoppableAsyncService(
            self.bot_client, log_events=True, error_timeout_sec=0.1
            )
        event_service.upper_threshold = 1.0

        with SymphonyApiMocker(True) as m:
            m.add_mock_events(events)
            
            with self.assertRaises(RuntimeError):
                _run(event_service.start_datafeed())
        