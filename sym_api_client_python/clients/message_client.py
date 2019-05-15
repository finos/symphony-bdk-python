import requests
import json
import logging
from .api_client import APIClient
from ..exceptions.UnauthorizedException import UnauthorizedException
from requests_toolbelt.multipart.encoder import MultipartEncoder


# child class of APIClient --> Extends error handling functionality
# MessageClient class contains a series of functions corresponding to all
# messaging endpoints on the REST API.
class MessageClient(APIClient):

    def __init__(self, bot_client):
        self.bot_client = bot_client

    def get_msg_from_stream(self, stream_id, since, **kwargs):
        logging.debug('MessageClient/get_msg_from_stream()')
        url = '/agent/v4/stream/{0}/message'.format(stream_id)
        params = {
            'since': since
        }
        params = params.update(kwargs)
        return self.bot_client.execute_rest_call('GET', url, params=params)

    def send_msg(self, stream_id, outbound_msg):
        logging.debug('MessageClient/send_msg()')
        url = '/agent/v4/stream/{0}/message/create'.format(stream_id)
        return self.bot_client.execute_rest_call('POST', url, files=outbound_msg)

    def send_msg_with_attachment(self, stream_id, msg,
                                 filename, path_to_attachment):
        logging.debug('MessageClient/send_msg_with_attachment()')
        url = '/agent/v4/stream/{0}/message/create'.format(stream_id)
        data = MultipartEncoder(
            fields={'message': msg,
                    'attachment': (
                    filename, open(path_to_attachment, 'rb'), 'file')}
        )
        headers = {
            'Content-Type': data.content_type
        }
        return self.bot_client.execute_rest_call("POST", url, data=data, headers=headers)

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
        params = params.update(kwargs)
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
