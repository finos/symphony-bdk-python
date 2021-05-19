import io
import logging
from contextlib import contextmanager
from typing import Union

from .api_client import APIClient

# child class of APIClient --> Extends error handling functionality
# MessageClient class contains a series of functions corresponding to all
# messaging endpoints on the REST API.

MESSAGE_STREAM_API = '/agent/v4/stream/{stream_id}/message'
MESSAGE_CREATE = MESSAGE_STREAM_API + '/create'


@contextmanager
def open_file(file):
    if isinstance(file, io.IOBase):
        # already opened file
        yield file
    else:
        try:
            file_object = open(file, mode='rb')
            yield file_object
        finally:
            file_object.close()


class MessageClient(APIClient):

    def __init__(self, bot_client):
        self.bot_client = bot_client

    def get_msg_from_stream(self, stream_id, since, **kwargs):
        logging.debug('MessageClient/get_msg_from_stream()')
        url = MESSAGE_STREAM_API.format(stream_id=stream_id)
        params = {
            'since': since
        }
        params.update(kwargs)
        return self.bot_client.execute_rest_call('GET', url, params=params)

    async def get_msg_from_stream_async(self, stream_id, since, **kwargs):
        logging.debug('MessageClient/get_msg_from_stream_async()')
        url = MESSAGE_STREAM_API.format(stream_id=stream_id)
        params = {
            'since': since
        }
        params.update(kwargs)
        return await self.bot_client.execute_rest_call_async('GET', url, params=params)

    def send_msg(self, stream_id, outbound_msg):
        logging.debug('MessageClient/send_msg()')
        url = MESSAGE_CREATE.format(stream_id=stream_id)
        return self.bot_client.execute_rest_call('POST', url, files=outbound_msg)

    async def send_msg_async(self, stream_id, outbound_msg):
        logging.debug('MessageClient/send_msg()')
        url = MESSAGE_CREATE.format(stream_id=stream_id)
        return await self.bot_client.execute_rest_call_async('POST', url, files=outbound_msg)

    def _data_and_headers_for_attachment(self, stream_id, msg, filename, attachment_file, aio=False):
        """Build an attachment out of either a path or a stream"""
        url = MESSAGE_CREATE.format(stream_id=stream_id)

        # The below states that Content-Type for attachments should be 'file' which is almost
        # certainly wrong - it's not a valid MIME-type. text/plain seems right
        fields = {'message': msg,
                  'attachment': (filename, attachment_file, "file")}

        parts = self.make_mulitpart_form(fields, aio=aio)

        return {'path': url, **parts}

    def send_msg_with_attachment(self, stream_id, msg,
                                 filename, attachment: Union[str, io.BytesIO]):
        """
        In this function make sure that msg parameter is set to just the messageML string.
        Do not set msg parameter to dict(message='<messageML>testing attachement</messageML>')
        for this function

        :param attachment:
            A path to a file or a stream of bytes.
        """
        logging.debug('MessageClient/send_msg_with_attachment()')
        with open_file(attachment) as attachment_file:
            parts = self._data_and_headers_for_attachment(stream_id, msg, filename, attachment_file)
            return self.bot_client.execute_rest_call("POST", **parts)

    async def send_msg_with_attachment_async(self, stream_id, msg,
                                             filename, attachment: Union[str, io.BytesIO]):
        """
        :param attachment:
            A path to a file or a stream of bytes.
        """
        logging.debug('MessageClient/send_msg_with_attachment()')
        with open_file(attachment) as attachment_file:
            parts = self._data_and_headers_for_attachment(stream_id, msg, filename, attachment_file, aio=True)
            return await self.bot_client.execute_rest_call_async('POST', **parts)

    def get_msg_attachment(self, stream_id, msg_id, file_id):
        logging.debug('MessageClient/get_msg_attachment()')
        url = '/agent/v1/stream/{0}/attachment'.format(stream_id)
        params = {
            'messageId': msg_id,
            'fileId': file_id
        }
        return self.bot_client.execute_rest_call("GET", url, params=params)

    # go on admin clients --> Contains sample data just for example's sake
    def import_message(self, importedMessage):
        logging.debug('MessageClient/import_message()')
        url = '/agent/v4/message/import'
        return self.bot_client.execute_rest_call("POST", url, json=importedMessage)

    # go on admin clients
    def suppress_message(self, id):
        logging.debug('MessageClient/suppress_message()')
        url = '/pod/v1/admin/messagesuppression/{0}/suppress'.format(id)
        return self.bot_client.execute_rest_call("POST", url)

    def post_msg_search(self, query, **kwargs):
        logging.debug('MessageClient/post_msg_search()')
        url = '/agent/v1/message/search'
        return self.bot_client.execute_rest_call("POST", url, json=query, params=kwargs)

    # contains sample query for example
    def get_msg_search(self, query, **kwargs):
        logging.debug('MessageClient/get_msg_search()')
        url = '/agent/v1/message/search'
        params = {
            'query': query
        }
        params.update(kwargs)
        return self.bot_client.execute_rest_call("GET", url, params=params)

    def get_msg_status(self, msg_id):
        logging.debug('MessageClient/get_msg_status()')
        url = '/pod/v1/message/{0}/status'.format(msg_id)
        return self.bot_client.execute_rest_call("GET", url)

    def get_supported_attachment_types(self):
        logging.debug('MessageClient/getAttachmentTypes()')
        url = '/pod/v1/files/allowedTypes'
        return self.bot_client.execute_rest_call("GET", url)

    def get_msg_ids_by_timestamp(self, msg_id, **kwargs):
        logging.debug('MessageClient/get_msg_ids_by_timestamp()')
        url = '/pod/v2/admin/streams/{0}/messageIds'.format(msg_id)
        return self.bot_client.execute_rest_call('GET', url, params=kwargs)

    def list_msg_receipts(self, msg_id):
        logging.debug('MessageClient/list_msg_receipts()')
        url = '/pod/v1/admin/messages/{0}/receipts'.format(msg_id)
        return self.bot_client.example('GET', url)

    def list_stream_attachments(self, stream_id):
        logging.debug('MessageClient/list_msg_attachments()')
        url = '/pod/v1/streams/{0}/attachments'.format(stream_id)
        return self.bot_client.execute_rest_call('GET', url)
