"""Testing the datafeed in various forms

The decision was taken not to fully mock out the datafeed due to the complexity of doing so,
however the events can be simulated.
"""

import asyncio
import logging
import re
import unittest
from unittest.mock import patch

from sym_api_client_python.loaders import load_from_env_var
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.listeners.im_listener import IMListener
from sym_api_client_python.exceptions.DatafeedExpiredException import DatafeedExpiredException
from sym_api_client_python.mocks.dummy_datafeed_service import (
    SymphonyApiMocker, StoppableService, StoppableAsyncService, make_error, make_events, READ_DATAFEED_URL, STOP_EVENT
)


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
            logging.error("Unable to find config from environment variables")
            #RSA Auth flow:
            cls.configure = SymConfig('sym_api_client_python/resources/config.json')
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
            m.add_mock_events([make_events(count=2), make_events([None, None, STOP_EVENT])],
                add_stop_event=False
            )

            event_service = StoppableService(self.bot_client)
            event_service.start_datafeed()

            datafeed_calls = [
                req for req in m.requests_mock_manager.request_history
                if READ_DATAFEED_URL.match(req.url)
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

def _run(coro):
    res = asyncio.get_event_loop().run_until_complete(coro)
    return res


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
            logging.error("Unable to find config from environment variables")
            #RSA Auth flow:
            cls.configure = SymConfig('sym_api_client_python/resources/config.json')
            cls.configure.load_config()
            cls.auth = SymBotRSAAuth(cls.configure)
            cls.auth.authenticate()
            conf, auth = load_from_env_var("SYMPHONY_TEST_CONFIG")
            cls.configure = conf
            cls.auth = auth

        # Initialize SymBotClient with auth and configure objects
        cls.bot_client = SymBotClient(cls.auth, cls.configure)

    def test_start_datafeed_and_stop(self):
        """Test the stop event works for the custom datafeed"""

        with SymphonyApiMocker(True) as m:

            m.add_mock_events([make_events([STOP_EVENT], aio=True)])

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
        