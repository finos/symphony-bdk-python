import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.reaction.reaction_service import (
    REACTIONS_PATH,
    ReactionService,
    to_padded_base64,
)
from symphony.bdk.gen.api_client import ApiClient
from tests.core.config import minimal_retry_config

URL_SAFE_ID = "XiIv3APOCgkFmgERKMwe8n___l7sy8bgbQ"
PADDED_ID = "XiIv3APOCgkFmgERKMwe8n///l7sy8bgbQ=="


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    bot_session = AuthSession(None)
    bot_session.session_token = "session_token"
    bot_session.key_manager_token = "km_token"
    return bot_session


@pytest.fixture(name="mocked_pod_client")
def fixture_mocked_pod_client():
    api_client = MagicMock(ApiClient)
    api_client.configuration = MagicMock()
    api_client.configuration.host = "https://acme.symphony.com"
    api_client.call_api = AsyncMock(return_value=MagicMock(data=None))
    return api_client


@pytest.fixture(name="reaction_service")
def fixture_reaction_service(mocked_pod_client, auth_session):
    return ReactionService(mocked_pod_client, auth_session, minimal_retry_config())


def last_call(mocked_pod_client):
    args, kwargs = mocked_pod_client.call_api.call_args
    body = kwargs.get("body")
    return args[0], args[1], kwargs.get("header_params"), json.loads(body) if body else None


class TestToPaddedBase64:
    def test_url_safe_id_is_converted(self):
        assert to_padded_base64(URL_SAFE_ID) == PADDED_ID

    def test_already_padded_id_is_unchanged(self):
        assert to_padded_base64(PADDED_ID) == PADDED_ID

    def test_non_base64_is_rejected(self):
        with pytest.raises(ValueError):
            to_padded_base64("not base64 at all!!")


@pytest.mark.asyncio
async def test_react_posts_emoji_and_padded_id(reaction_service, mocked_pod_client):
    await reaction_service.react(URL_SAFE_ID, "\N{THUMBS UP SIGN}")

    method, url, headers, body = last_call(mocked_pod_client)
    assert method == "POST"
    assert url == "https://acme.symphony.com" + REACTIONS_PATH
    assert headers["sessionToken"] == "session_token"
    assert body["messageId"] == PADDED_ID
    assert body["emoji"] == "\N{THUMBS UP SIGN}"
    assert isinstance(body["timestamp"], int)


@pytest.mark.asyncio
async def test_react_rejects_an_empty_emoji(reaction_service, mocked_pod_client):
    for empty in ("", "   "):
        with pytest.raises(ValueError):
            await reaction_service.react(URL_SAFE_ID, empty)
    mocked_pod_client.call_api.assert_not_called()


@pytest.mark.asyncio
async def test_unreact_omits_the_emoji_field(reaction_service, mocked_pod_client):
    """The pod rejects an empty emoji, so clearing has to leave the field out."""
    await reaction_service.unreact(URL_SAFE_ID)

    method, _, _, body = last_call(mocked_pod_client)
    assert method == "POST"
    assert "emoji" not in body
    assert body["messageId"] == PADDED_ID


@pytest.mark.asyncio
async def test_list_reactions_returns_the_mapping(reaction_service, mocked_pod_client):
    payload = {"reactions": {"\N{THUMBS UP SIGN}": [{"userId": 1234, "ts": 1}]}, "sequenceNb": 1}
    mocked_pod_client.call_api = AsyncMock(return_value=MagicMock(data=json.dumps(payload)))

    reactions = await reaction_service.list_reactions(URL_SAFE_ID)

    assert reactions == payload["reactions"]
    method, url, _, body = last_call(mocked_pod_client)
    assert method == "GET"
    assert body is None
    assert "initialMessageId=XiIv3APOCgkFmgERKMwe8n%2F%2F%2Fl7sy8bgbQ%3D%3D" in url


@pytest.mark.asyncio
async def test_list_reactions_handles_an_empty_response(reaction_service, mocked_pod_client):
    mocked_pod_client.call_api = AsyncMock(return_value=MagicMock(data=None))

    assert await reaction_service.list_reactions(URL_SAFE_ID) == {}
