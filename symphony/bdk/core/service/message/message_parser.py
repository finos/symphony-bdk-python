"""This module contains a set of util functions that can be used on incoming V4Message such as:
extracting entities like Mentions, Hashtags, Cashtags, Emojis and extracting text content from presentationML
contained in the message.
"""
import json

from enum import Enum
from json import JSONDecodeError
from typing import Dict
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ElementTree, fromstring, tostring

from symphony.bdk.core.service.exception import MessageParserError
from symphony.bdk.gen.agent_model.v4_message import V4Message


def get_text_content_from_message(message: V4Message) -> str:
    """Get text content from PresentationML on incoming messages

    :param message: message containing the PresentationML to be parsed
    :return: the message text content extracted from the given PresentationML
    """

    presentation_ml = message.message
    try:
        tree = ElementTree(fromstring(presentation_ml))
    except ET.ParseError as exc:
        raise MessageParserError("Unable to parse the PresentationML, it is not in the correct format.") from exc
    return tostring(tree.getroot(), method="text").decode().strip()


def get_mentions(message: V4Message) -> [int]:
    """ Parse data inside an incoming message and returns a list containing the user ids corresponding
    to the users mentioned

    :param message: incoming V4 message to be parsed
    :return: list of users ids that has been mentioned inside the message
    """
    mentions_list = _get_tags(message, _EntityTypeEnum.MENTION)
    return [int(user_id) for user_id in mentions_list]


def get_hashtags(message: V4Message) -> [str]:
    """ Parse data inside an incoming message and returns a list containing the text of the hashtags found

    :param message: message incoming V4 message to be parsed
    :return: list of hashtags contained in the message
    """
    return _get_tags(message, _EntityTypeEnum.HASHTAG)


def get_cashtags(message: V4Message) -> [str]:
    """ Parse data inside an incoming message and returns a list containing the text of the cashtags found

    :param message: message incoming V4 message to be parsed
    :return: list of cashtags contained in the message
    """
    return _get_tags(message, _EntityTypeEnum.CASHTAG)


def get_emojis(message: V4Message) -> Dict[str, str]:
    """ Parse data inside an incoming message and returns a map containing the list of emojis found.
    Key of the map are the annotation used to identify the emoji and the values are the their unicode.

    :param message: message incoming V4 message to be parsed
    :return: list of cashtags contained in the message
    """
    json_data = _parse_json_data(message.data)
    emojis_list = {}
    for item in json_data.values():
        try:
            if item["type"] == _EntityTypeEnum.EMOJI.value:
                emojis_list[item["data"]["annotation"]] = item["data"]["unicode"]
        except KeyError:
            pass
    return emojis_list


def _get_tags(message, entity_type):
    json_data = _parse_json_data(message.data)
    tags_list = []
    for item in json_data.values():
        try:
            if item["type"] == entity_type.value:
                tags_list.append(item["id"][0]["value"])
        except KeyError:
            pass
    return tags_list


def _parse_json_data(json_data):
    try:
        return json.loads(json_data)
    except JSONDecodeError as exc:
        raise MessageParserError("Failed to extract payload from message data") from exc


class _EntityTypeEnum(Enum):
    HASHTAG = "org.symphonyoss.taxonomy"
    CASHTAG = "org.symphonyoss.fin.security"
    MENTION = "com.symphony.user.mention"
    EMOJI = "com.symphony.emoji"
