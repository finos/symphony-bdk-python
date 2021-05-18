import json
from typing import List, Tuple, Union, IO

from symphony.bdk.core.service.exception import MessageCreationError

MESSAGE_ML_END_TAG = "</messageML>"
MESSAGE_ML_START_TAG = "<messageML>"


class Message:
    """Class holding message information, used in
    :py:class:`~symphony.bdk.core.service.message.message_service.MessageService` to send a message.
    To know more about the format, see
    `Create Message <https://developers.symphony.com/restapi/reference#create-message-v4>`_.
    """

    def __init__(self, content: str, data=None,
                 attachments: List[Union[IO, Tuple[IO, IO]]] = None, version: str = ""):
        """Builds a message.

        :param content: the MessageML content to be sent. This is mandatory
          If there is no <messageML> tags, they will be added to the content.
        :param data: an object (e.g. dict) that will be serialized into JSON using ``json.dumps``
        :param attachments: list of attachments or list of (attachment, previews).
          These must be opened files either in binary or text mode.
          Previews are optional but if present, all attachments must have a preview.
        :param version: Optional message version in the format "major.minor".
          If empty, defaults to the latest supported version.
        :raise MessageCreationError: if content is None,
          or if number of previews different than the number of attachments (in case there is at least one preview).
        """
        self._content = self._get_content(content)
        self._data = "" if data is None else json.dumps(data)
        self._version = version
        self._attachments, self._previews = self._get_attachments_and_previews(attachments)

    @property
    def content(self) -> str:
        """Message content

        :return: the messageML content
        """
        return self._content

    @property
    def data(self) -> str:
        """Message data

        :return: the data as a JSON string
        """
        return self._data

    @property
    def version(self) -> str:
        """Message format version.

        :return: the message format version
        """
        return self._version

    @property
    def attachments(self) -> List[IO]:
        """List of attachments

        :return: the list of attachments
        """
        return self._attachments

    @property
    def previews(self) -> List[IO]:
        """List of previews

        :return: the list of previews
        """
        return self._previews

    @staticmethod
    def _get_content(content):
        if content is None:
            raise MessageCreationError("Message content is mandatory")
        if not content.startswith(MESSAGE_ML_START_TAG) and not content.endswith(MESSAGE_ML_END_TAG):
            return MESSAGE_ML_START_TAG + content + MESSAGE_ML_END_TAG
        return content

    @staticmethod
    def _get_attachments_and_previews(attachments_previews):
        if attachments_previews is None:
            return [], []

        attachments = []
        previews = []
        for item in attachments_previews:
            if isinstance(item, tuple) and len(item) >= 1:
                attachments.append(item[0])
                if len(item) >= 2:
                    previews.append(item[1])
            else:
                attachments.append(item)

        if previews and len(previews) != len(attachments):
            raise MessageCreationError("Message should contain either no preview or as many previews as attachments")

        return attachments, previews
