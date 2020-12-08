import asyncio
from unittest import TestCase, mock, IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock

import pytest

from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.datafeed_event_service import AsyncDataFeedEventService
from sym_api_client_python.listeners.im_listener import IMListener
from tests.clients.test_datafeed_client import get_path_relative_to_resources_folder


class TestDataFeedEventService(IsolatedAsyncioTestCase):

    def setUp(self):
        self.config = SymConfig(get_path_relative_to_resources_folder('./bot-config.json'))
        self.config.load_config()
        self.client = SymBotClient(None, self.config)
        self.ran = False

    @mock.patch(
        'sym_api_client_python.clients.datafeed_client.DataFeedClient',
        new_callable=AsyncMock)
    async def test_read_datafeed_event_no_id(self, datafeed_client_mock):
        self.service = AsyncDataFeedEventService(self.client)
        self.client.get_bot_user_info = MagicMock(return_value={'id': 456})

        self.service.datafeed_client = datafeed_client_mock
        datafeed_client_mock.read_datafeed_async.side_effect = self.return_event_no_id_first_time

        listener = IMListenerRecorder(self.service)
        self.service.add_im_listener(listener)

        # Simulate start_datafeed
        await asyncio.gather(self.service.read_datafeed(), self.service.handle_events())

        self.assertIsNotNone(listener.last_message)

    async def return_event_no_id_first_time(self, _arg):
        if self.ran:
            # Give control back to handle_event coroutine
            await asyncio.sleep(0)
            return []

        else:
            self.ran = True
            event = {'type': 'MESSAGESENT', 'timestamp': 0,
                     'payload': {'messageSent': {'message': {'stream': {'streamType': 'IM'}}}},
                     'initiator': {'user': {'userId': 123}}}
            return [event]


class IMListenerRecorder(IMListener):

    def __init__(self, service) -> None:
        super().__init__()
        self.service = service
        self.last_message = None

    async def on_im_message(self, message):
        self.last_message = message
        # Stop datafeed loop
        await self.service.deactivate_datafeed(False)

    def on_im_created(self, stream):
        pass  # Not used
