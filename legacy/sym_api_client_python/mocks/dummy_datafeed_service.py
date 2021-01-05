"""Dummy datafeed services for testing bots

Originally these dummy datafeeds were solely used in the tests, however it was deemed that they might
be of use to downstream clients who want to test their own bots in the same way that they are tested
in the API.

Some of the methods in the SDK use requests, and some use aiohttp, therefore to stub out both of them
two mocking libraries are used. It would have been preferable to mock both types of method with one
library but the only one that offered that possibility was Mocket. Mocket doesn't support regex path
matching and dynamic responses. requests-mock and aioresponses were chosen, the Datafeed mocker wraps
both of these.

To see examples of how things mocks are used, check the tests in test_datafeed.py
"""

import asyncio
import copy
import logging
import re
import uuid
from itertools import count

import requests_mock
from aioresponses import aioresponses, CallbackResult

from sym_api_client_python.datafeed_event_service import DataFeedEventService, AsyncDataFeedEventService

STOP_EVENT = 'TEST_STOP_EVENT'
READ_DATAFEED_URL = re.compile('^.*/agent/v4/datafeed/.*/read')

_CREATE_DATAFEED_URL = '/agent/v4/datafeed/create'
_SESSION_INFO = '/pod/v2/sessioninfo'

BASIC_EVENT = {
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
    requests and aioresponses for the mocking.

    Example usage:

        event_service = StoppableService(self.bot_client)
        events = [make_events(count=2)]

        with SymphonyApiMocker() as m:
            m.add_mock_events(events)
            event_service.start_datafeed()

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
        """Add a list of events to the mocker. It's expected that most of the time a terminating
        stop event is desired, otherwise the datafeed_read will block forever. If it's not
        required pass add_stop_event=False
        """

        if self.aio:
            # Mock for aioreponses
            for events in events_list:
                self.aioresponses_manager.get(READ_DATAFEED_URL, **events)

            if add_stop_event:
                self.aioresponses_manager.get(
                    READ_DATAFEED_URL, **make_events([STOP_EVENT], aio=True)
                )
                self.aioresponses_manager.get(
                    READ_DATAFEED_URL, callback=make_timed_callback(5), repeat=True
                )
        else:
            if add_stop_event:
                events_list.append(make_events([STOP_EVENT]))
            # anyrequest that goes through this url will return events_list
            # find event list
            self.requests_mock_manager.register_uri('GET', READ_DATAFEED_URL, events_list)

    def dummy_id_provider(self):
        counter = count(1)

        def f(*args, _counter=counter, **kwargs):
            feed_response = {
                "id": "DUMMY-DATAFEED-ID-{}".format(next(_counter))
            }
            return feed_response

        return f


def make_events(event_types=None, count=None, messages=None, aio=False):
    """Returns a dict to be consumed by the SymphonyApiMocker, specifically for the
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
        event = copy.deepcopy(BASIC_EVENT)

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
    """Returns an error as a dict to be consumed by the SymphonyApiMocker like:
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


def make_timed_callback(sleep_time=1):
    """Simulate the behaviour of the server, blocking for 30s and return a 204. Instead
    of waiting 30s by default it just waits 1"""

    async def timed_callback(url, **kwargs):
        await asyncio.sleep(sleep_time)
        return CallbackResult(status=204)

    return timed_callback


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

        if STOP_EVENT not in self.routing_dict:
            self.routing_dict[STOP_EVENT] = self._stop_feed_handler
        else:
            raise KeyError(f"Dummy stop event {STOP_EVENT} already exists as a regular event")

    def _stop_feed_handler(self, payload):
        self.deactivate_datafeed()


class StoppableAsyncService(AsyncDataFeedEventService):
    """While other strategies could be employed to stop the async services, it's simpler for the
    purposes of these tests to keep the sync model.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if STOP_EVENT not in self.routing_dict:
            self.routing_dict[STOP_EVENT] = self._stop_feed_handler
        else:
            raise KeyError(f"Dummy stop event {STOP_EVENT} already exists as a regular event")

    async def _stop_feed_handler(self, payload):
        asyncio.ensure_future(self.deactivate_datafeed())
