import json

import pytest

from symphony.bdk.core.service.exception import MessageCreationError
from symphony.bdk.core.service.message.model import Message


def assert_message_properties_equal(actual_message, expected_content, expected_data, expected_version,
                                    expected_attachments, expected_previews):
    assert actual_message.content == expected_content
    assert actual_message.data == expected_data
    assert actual_message.version == expected_version
    assert actual_message.attachments == expected_attachments
    assert actual_message.previews == expected_previews


def test_create_message_with_no_content():
    with pytest.raises(MessageCreationError):
        Message(content=None)


def test_create_message_content_only_without_tags():
    assert_message_properties_equal(Message(content="Hello world!"),
                                    "<messageML>Hello world!</messageML>", "", "", [], [])


def test_create_message_content_only():
    content = "<messageML>Hello world!</messageML>"

    assert_message_properties_equal(Message(content=content),
                                    content, "", "", [], [])


def test_create_message_content_data_version():
    content = "<messageML>Hello world!</messageML>"
    version = "2.0"
    data = ['foo', {'bar': ('baz', 1.0, 2)}]
    json_data = json.dumps(data)

    assert_message_properties_equal(Message(content=content, version=version, data=data),
                                    content, json_data, version, [], [])


def test_create_message_with_attachment():
    content = "<messageML>Hello world!</messageML>"
    attachments = ["some attachment"]

    assert_message_properties_equal(Message(content=content, attachments=attachments),
                                    content, "", "", attachments, [])


def test_create_message_with_attachment_one_element_tuple():
    content = "<messageML>Hello world!</messageML>"
    attachment = "some attachment"

    assert_message_properties_equal(Message(content=content, attachments=[(attachment,)]),
                                    content, "", "", [attachment], [])


def test_create_message_with_attachment_and_preview():
    content = "<messageML>Hello world!</messageML>"
    attachment = "some attachment"
    preview = "some preview"
    assert_message_properties_equal(Message(content=content, attachments=[(attachment, preview)]),
                                    content, "", "", [attachment], [preview])


def test_create_message_with_attachment_and_no_preview_for_second_attachment():
    with pytest.raises(MessageCreationError):
        Message(content="<messageML>Hello world!</messageML>",
                attachments=[("first attachment", "first preview"), "second attachment"])


def test_create_message_with_attachment_and_no_preview_for_first_attachment():
    with pytest.raises(MessageCreationError):
        Message(content="<messageML>Hello world!</messageML>",
                attachments=["first attachment", ("second attachment", "second preview")])
