from unittest.mock import MagicMock

import pytest

from symphony.bdk.core.service.exception import MessageParserError
from symphony.bdk.core.service.message.message_parser import (
    get_cashtags,
    get_emojis,
    get_hashtags,
    get_mentions,
    get_text_content_from_message,
)
from symphony.bdk.gen.agent_model.v4_message import V4Message
from tests.utils.resource_utils import get_resource_content


def create_v4_message(message, data=None):
    v4_message = MagicMock(V4Message)
    v4_message.data = data
    v4_message.message = message
    return v4_message


def assert_message_has_text_content(actual_message, expected_text_content):
    assert get_text_content_from_message(actual_message) == expected_text_content


@pytest.fixture(name="message_with_data")
def fixture_message_with_data():
    return create_v4_message(
        '<div data-format="PresentationML" data-version="2.0"> \n'
        '<a href="http://www.symphony.com">This is a link to Symphony\'s Website</a> \n </div>',
        get_resource_content("utils/message_entity_data.json"),
    )


@pytest.fixture(name="message_with_invalid_data")
def fixture_message_with_invalid_data():
    return create_v4_message(
        '<div data-format="PresentationML" data-version="2.0"> \n', "unparsable json data"
    )


def test_get_text_content_from_message():
    message = create_v4_message(
        '<div data-format="PresentationML" data-version="2.0"> \n'
        '<a href="http://www.symphony.com">This is a link to Symphony\'s Website</a> \n </div>'
    )
    assert_message_has_text_content(message, "This is a link to Symphony's Website")


def test_get_text_content_from_escaped_message_ampersand():
    escaped_message_ampersand = create_v4_message(
        '<div data-format="PresentationML" data-version="2.0"> \n'
        "This is some escaped text &amp;</div>"
    )
    assert_message_has_text_content(escaped_message_ampersand, "This is some escaped text &")


def test_get_text_content_from_escaped_message_lt():
    escaped_message_lt = create_v4_message(
        '<div data-format="PresentationML" data-version="2.0"> \n'
        "This is some escaped text &lt;</div>"
    )
    assert_message_has_text_content(escaped_message_lt, "This is some escaped text <")


def test_get_text_content_from_message_with_html_entities():
    message_with_nbsp = create_v4_message(
        '<div data-format="PresentationML" data-version="2.0"> \n'
        "This is some escaped text &nbsp;</div>"
    )
    with pytest.raises(MessageParserError):
        get_text_content_from_message(message_with_nbsp)


def test_get_text_content_from_message_invalid_json_data(message_with_invalid_data):
    with pytest.raises(MessageParserError):
        get_text_content_from_message(message_with_invalid_data)


def test_get_mentions(message_with_data):
    mentions = get_mentions(message_with_data)
    assert len(mentions) == 2
    assert mentions[0] == 13056700580915
    assert mentions[1] == 1305690252351


def test_get_hashtags(message_with_data):
    hashtags = get_hashtags(message_with_data)
    assert len(hashtags) == 1
    assert hashtags[0] == "bot"


def test_get_cashtags(message_with_data):
    cashtags = get_cashtags(message_with_data)
    assert len(cashtags) == 1
    assert cashtags[0] == "hello"


def test_get_emojis(message_with_data):
    emojis = get_emojis(message_with_data)
    assert emojis == {"grinning": "😀"}


def test_get_tags_unparsable_data(message_with_invalid_data):
    with pytest.raises(MessageParserError):
        get_emojis(message_with_invalid_data)
