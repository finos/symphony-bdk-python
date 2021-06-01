from unittest.mock import MagicMock

import pytest

from symphony.bdk.core.service.exception import MessageParserError
from symphony.bdk.core.service.message.message_parser import get_text_content_from_message, get_mentions, \
    get_hashtags, get_cashtags, get_emojis
from symphony.bdk.gen.agent_model.v4_message import V4Message
from tests.utils.resource_utils import get_resource_content


@pytest.fixture(name="message")
def fixture_message():
    message = MagicMock(V4Message)
    message.data = get_resource_content("utils/message_entity_data.json")
    message.message = "<div data-format=\"PresentationML\" data-version=\"2.0\"> \n" \
                      "<a href=\"http://www.symphony.com\">This is a link to Symphony's Website</a> \n </div>"
    return message


@pytest.fixture(name="unparsable_message")
def fixture_unparsable_message():
    message = MagicMock(V4Message)
    message.data = "unparsable json data"
    message.message = "<div data-format=\"PresentationML\" data-version=\"2.0\"> \n"
    return message


def test_get_text_content_from_message(message):
    plain_text = get_text_content_from_message(message)
    assert plain_text == "This is a link to Symphony's Website"


def test_get_text_content_from_message_unparsable(unparsable_message):
    with pytest.raises(MessageParserError):
        get_text_content_from_message(unparsable_message)


def test_get_mentions(message):
    mentions = get_mentions(message)
    assert len(mentions) == 2
    assert mentions[0] == 13056700580915
    assert mentions[1] == 1305690252351


def test_get_hashtags(message):
    hashtags = get_hashtags(message)
    assert len(hashtags) == 1
    assert hashtags[0] == "bot"


def test_get_cashtags(message):
    cashtags = get_cashtags(message)
    assert len(cashtags) == 1
    assert cashtags[0] == "hello"


def test_get_emojis(message):
    emojis = get_emojis(message)
    assert emojis == {"grinning": "😀"}


def test_get_tags_unparsable_data(unparsable_message):
    unparsable_message.data = "unparsable_json"
    with pytest.raises(MessageParserError):
        get_emojis(unparsable_message)
