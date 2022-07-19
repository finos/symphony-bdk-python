import json
import re

from defusedxml.ElementTree import fromstring

from symphony.bdk.core.activity.parsing.message_entities import Cashtag, Hashtag, Mention
from symphony.bdk.gen.agent_model.v4_message import V4Message


class InputTokenizer:
    """
    Class responsible for parsing a {@link V4Message} into a list of tokens separated by at least one whitespace
    character.
    Tokens can be of type {@link String}, {@link Mention}, {@link Cashtag} or {@link Hashtag} depending on the message
    content.
    """

    whitespace_pattern = re.compile(r"\s+")
    data_entity_id = "data-entity-id"

    def __init__(self, message: V4Message):
        """
        :param message: message to be tokenized.
        """
        self._document = fromstring(message.message)
        json_data = message.data if hasattr(message, 'data') and message.data else "{}"
        self._data_node = json.loads(json_data)
        self._buffer = ""
        self._tokens = []
        self._parse_xml_text(self._document)

        self._parse_buffer()

    def _parse_buffer(self):
        for item in re.split(InputTokenizer.whitespace_pattern, self._buffer):
            if item:
                self._tokens.append(item)

        # clear the buffer
        self._buffer = ""

    def _parse_xml_text(self, root):
        if self._is_entity_node(root):
            self._parse_buffer()
            entity_id = root.attrib[InputTokenizer.data_entity_id]
            entity_type = self._data_node[entity_id]['type']
            if self._is_entity_type_supported(entity_type):
                self._parse_entity_node(entity_id, root)
            else:
                self._parse_text(root)
        else:
            self._parse_text(root)

        if root.tail:
            self._parse_buffer()
            self._buffer += root.tail
        else:
            self._parse_buffer()

    def _parse_entity_node(self, entity_id, root):
        """
        Parses an entity node content and fill the tokens array.

        :param entity_id: entity id to be parsed
        :param root: root of the xml document
        :return:
        """
        for item in self._data_node[entity_id]["id"]:
            if item["type"] == "org.symphonyoss.taxonomy.hashtag":
                self._tokens.append(Hashtag(root.text, item["value"]))
            elif item["type"] == "org.symphonyoss.fin.security.id.ticker":
                self._tokens.append(Cashtag(root.text, item["value"]))
            elif item["type"] == "com.symphony.user.userId":
                self._tokens.append(Mention(root.text, int(item["value"])))

    def _parse_text(self, root):
        """
        Parses the node, fills the text buffer and parses the subsequent nodes.

        :param root: root of the xml document
        """
        if root.text:
            self._buffer += root.text
        for child in root:
            self._parse_xml_text(child)

    def _is_entity_node(self, root):
        """
        Checks if the node is a known entity.

        :param root: root of the xml document
        :return: Whether the node is a known entity.
        """
        if root.tag == "span" and "class" in root.attrib and root.attrib["class"] == "entity" \
                and InputTokenizer.data_entity_id in root.attrib:
            return root.attrib[InputTokenizer.data_entity_id] in self._data_node
        return False

    @staticmethod
    def _is_entity_type_supported(entity_type):
        return entity_type in ["org.symphonyoss.taxonomy", "org.symphonyoss.fin.security", "com.symphony.user.mention"]

    @property
    def tokens(self):
        return self._tokens
