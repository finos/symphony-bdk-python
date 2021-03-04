from unittest.mock import MagicMock, AsyncMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.signal.signal_service import SignalService
from symphony.bdk.gen.agent_api.signals_api import SignalsApi
from symphony.bdk.gen.agent_model.base_signal import BaseSignal
from tests.utils.resource_utils import object_from_json_relative_path, object_from_json


@pytest.fixture()
def auth_session():
    bot_session = AuthSession(None)
    bot_session.session_token = 'session_token'
    bot_session.key_manager_token = 'km_token'
    return bot_session


@pytest.fixture()
def signals_api():
    return MagicMock(SignalsApi)


@pytest.fixture()
def signal_service(signals_api, auth_session):
    service = SignalService(signals_api, auth_session)
    return service


@pytest.mark.asyncio
async def test_list_signals(signals_api, signal_service):
    signals_api.v1_signals_list_get = AsyncMock()
    signals_api.v1_signals_list_get.return_value = \
        object_from_json_relative_path('signal/list_signals.json')

    signal_list = await signal_service.list_signals()

    signals_api.v1_signals_list_get.assert_called_with(
        skip=0,
        limit=50,
        session_token='session_token',
        key_manager_token='km_token'
    )

    assert len(signal_list) == 2
    assert signal_list[0].id == 'signal_id1'


@pytest.mark.asyncio
async def test_list_signals_with_skip_and_limit(signals_api, signal_service):
    signals_api.v1_signals_list_get = AsyncMock()
    signals_api.v1_signals_list_get.return_value = \
        object_from_json_relative_path('signal/list_signals.json')

    signal_list = await signal_service.list_signals(3, 30)

    signals_api.v1_signals_list_get.assert_called_with(
        skip=3,
        limit=30,
        session_token='session_token',
        key_manager_token='km_token'
    )

    assert len(signal_list) == 2
    assert signal_list[0].id == 'signal_id1'


@pytest.mark.asyncio
async def test_get_signal(signals_api, signal_service):
    signals_api.v1_signals_id_get_get = AsyncMock()
    signals_api.v1_signals_id_get_get.return_value = \
        object_from_json_relative_path('signal/create_signal.json')

    signal = await signal_service.get_signal('signal_id')

    signals_api.v1_signals_id_get_get.assert_called_with(
        id='signal_id',
        session_token='session_token',
        key_manager_token='km_token'
    )

    assert signal.id == 'signal_id'
    assert signal.name == 'hash and cash'
    assert signal.query == 'HASHTAG:hash AND CASHTAG:cash'


@pytest.mark.asyncio
async def test_create_signal(signals_api, signal_service):
    signals_api.v1_signals_create_post = AsyncMock()
    signals_api.v1_signals_create_post.return_value = \
        object_from_json_relative_path('signal/create_signal.json')

    signal = await signal_service.create_signal(BaseSignal())

    signals_api.v1_signals_create_post.assert_called_with(
        signal=BaseSignal(),
        session_token='session_token',
        key_manager_token='km_token'
    )
    assert signal.id == 'signal_id'
    assert signal.name == 'hash and cash'
    assert signal.query == 'HASHTAG:hash AND CASHTAG:cash'


@pytest.mark.asyncio
async def test_update_signal(signals_api, signal_service):
    signals_api.v1_signals_id_update_post = AsyncMock()
    signals_api.v1_signals_id_update_post.return_value = \
        object_from_json_relative_path('signal/update_signal.json')

    signal = await signal_service.update_signal('signal_id', BaseSignal())

    signals_api.v1_signals_id_update_post.assert_called_with(
        id='signal_id',
        signal=BaseSignal(),
        session_token='session_token',
        key_manager_token='km_token'
    )

    assert signal.id == 'signal_id'
    assert signal.name == 'hash and cash updated'


@pytest.mark.asyncio
async def test_delete_signal(signals_api, signal_service):
    return_value = '{ "format": "TEXT", "message": "Signal signal_id deleted"}'
    signals_api.v1_signals_id_delete_post = AsyncMock()
    signals_api.v1_signals_id_delete_post.return_value = object_from_json(return_value)

    response = await signal_service.delete_signal('signal_id')

    signals_api.v1_signals_id_delete_post.assert_called_with(
        id='signal_id',
        session_token='session_token',
        key_manager_token='km_token'
    )

    assert response.message == 'Signal signal_id deleted'


@pytest.mark.asyncio
async def test_subscribe_users_to_signal(signals_api, signal_service):
    signals_api.v1_signals_id_subscribe_post = AsyncMock()
    signals_api.v1_signals_id_subscribe_post.return_value = \
        object_from_json_relative_path('signal/subscribe_signal.json')
    user_ids = [123, 465, 789]

    channel_subscription_response = await signal_service.subscribe_users_to_signal(
        'signal_id', True, user_ids)

    signals_api.v1_signals_id_subscribe_post.assert_called_with(
        id='signal_id',
        pushed=True,
        users=user_ids,
        session_token='session_token',
        key_manager_token='km_token'
    )

    assert channel_subscription_response.requestedSubscription == 3
    assert len(channel_subscription_response.subscriptionErrors) == 0


@pytest.mark.asyncio
async def test_unsubscribe_users_to_signal(signals_api, signal_service):
    signals_api.v1_signals_id_unsubscribe_post = AsyncMock()
    signals_api.v1_signals_id_unsubscribe_post.return_value = \
        object_from_json_relative_path('signal/subscribe_signal.json')
    user_ids = [123, 465, 789]

    channel_subscription_response = await signal_service.unsubscribe_users_to_signal(
        'signal_id', user_ids)

    signals_api.v1_signals_id_unsubscribe_post.assert_called_with(
        id='signal_id',
        users=user_ids,
        session_token='session_token',
        key_manager_token='km_token'
    )

    assert channel_subscription_response.requestedSubscription == 3
    assert len(channel_subscription_response.subscriptionErrors) == 0


@pytest.mark.asyncio
async def test_list_subscribers(signals_api, signal_service):
    signals_api.v1_signals_id_subscribers_get = AsyncMock()
    signals_api.v1_signals_id_subscribers_get.return_value = \
        object_from_json_relative_path('signal/list_subscribers.json')

    channel_subscribers = await signal_service.list_subscribers('signal_id')

    signals_api.v1_signals_id_subscribers_get.assert_called_with(
        id='signal_id',
        skip=0,
        limit=50,
        session_token='session_token',
        key_manager_token='km_token'
    )

    assert channel_subscribers.total == 150
    assert len(channel_subscribers.data) == 3


@pytest.mark.asyncio
async def test_list_subscribers_with_skip_and_limit(signals_api, signal_service):
    signals_api.v1_signals_id_subscribers_get = AsyncMock()
    signals_api.v1_signals_id_subscribers_get.return_value = \
        object_from_json_relative_path('signal/list_subscribers.json')

    channel_subscribers = await signal_service.list_subscribers('signal_id', 1, 10)

    signals_api.v1_signals_id_subscribers_get.assert_called_with(
        id='signal_id',
        skip=1,
        limit=10,
        session_token='session_token',
        key_manager_token='km_token'
    )

    assert channel_subscribers.total == 150
    assert len(channel_subscribers.data) == 3

