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
        self.config = self.bot_client.get_sym_config()

    def get_msg_from_stream(self, stream_id, since):
        logging.debug('MessageClient/getMessages()')
        url = '/agent/v4/stream/{0}/message?since={1}'.format(stream_id, since)
        return self.bot_client.execute_rest_call('GET', url)

    def send_msg(self, stream_id, outbound_msg):
        print(stream_id + " streamID to play with")
        logging.debug('MessageClient/createMessage()')
        url = '/agent/v4/stream/{0}/message/create'.format(stream_id)
        return self.bot_client.execute_rest_call('POST', url, files=outbound_msg)

    def send_msg_with_attachment(self, stream_id, msg,
                                 filename, path_to_attachment):
        url = '/agent/v4/stream/{0}/message/create'.format(stream_id)
        print(url)
        data = MultipartEncoder(
            fields={'message': msg,
                    'attachment': (
                    filename, open(path_to_attachment, 'rb'), 'file')}
        )
        headers = {
            'Content-Type': data.content_type
        }
        return self.bot_client.execute_rest_call("POST", url, data=data, headers=headers)

    def get_msg_attachments(self, stream_id, msg_id, file_id):
        logging.debug('MessageClient/getAttachments()')
        url = '/agent/v1/stream/{0}/attachment?msg_id={1}&file_id={2}'.format(stream_id, msg_id, file_id)
        return self.bot_client.execute_rest_call("GET", url)

    # go on admin clients --> Contains sample data just for example's sake
    def import_message(self):
        logging.debug('MessageClient/import_message()')
        url = '/agent/v4/message/import'
        data = {
            "message": "<messageML>Imported message</messageML>",
            "format": "MESSAGEML",
            "intendedMessageTimestamp": 1433045622000,
            "intendedMessageFromUserId": 7215545057281,
            "originatingSystemId": "",
            "originalMessageId": "",
            "streamId": ""
        }
        return self.bot_client.execute_rest_call("POST", url, data=data)

    # go on admin clients
    def suppress_message(self, id):
        logging.debug('MessageClient/suppress_message()')
        url = '/pod/v1/admin/messagesuppression/{0}/suppress'.format(id)
        return self.bot_client.execute_rest_call("POST", url)

    def post_msg_search(self):
        logging.debug('MessageClient/post_msg_search()')
        url = '/agent/v1/message/search'
        data = {
            'hashtag': 'reed'
        }
        return self.bot_client.execute_rest_call("POST", url, json=data)

    # contains sample query for example
    def get_msg_search(self):
        logging.debug('MessageClient/get_msg_search()')
        url = '/agent/v1/message/search'
        query = {
            'query': 'hashtag:reed'
        }
        return self.bot_client.execute_rest_call("GET", url, params=query)

    def get_msg_status(self, msg_id):
        logging.debug('MessageClient/get_msg_status()')
        url = '/pod/v1/message/{0}/status'.format(msg_id)
        return self.bot_client.execute_rest_call("GET", url)

    def get_supported_attachment_types(self):
        logging.debug('MessageClient/getAttachmentTypes()')
        url = '/pod/v1/files/allowedTypes'
        return self.bot_client.execute_rest_call("GET", url)
