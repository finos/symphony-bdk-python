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
        self.agent_proxies = self.config.data['agentProxyRequestObject']
        self.pod_proxies = self.config.data['podProxyRequestObject']
        
    def get_msg_from_stream(self, stream_id, since):
        logging.debug('MessageClient/getMessages()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token(),
            'keyManagerToken': self.bot_client.get_sym_auth().get_key_manager_token()
        }
        url = self.config.data['agentHost'] + \
              '/agent/v4/stream/{0}/message?since={1}'.format(stream_id, since)
        response = requests.get(url, headers=headers, proxies=self.agent_proxies)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_msg_from_stream(stream_id, since)

    def send_msg(self, stream_id, outbound_msg):
        print(stream_id + " streamID to play with")
        logging.debug('MessageClient/createMessage()')
        url = self.config.data['agentHost'] + \
              '/agent/v4/stream/{0}/message/create'.format(stream_id)
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token(),
            'keyManagerToken': self.bot_client.get_sym_auth().get_key_manager_token()
        }
        response = requests.post(url, files=outbound_msg,
                                 headers=headers, proxies=self.agent_proxies)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.send_msg(stream_id, outbound_msg)

    def send_msg_with_attachment(self, stream_id, msg,
                                 filename, path_to_attachment):
        url = self.config.data['agentHost'] + \
              '/agent/v4/stream/{0}/message/create'.format(stream_id)
        print(url)
        data = MultipartEncoder(
            fields={'message': msg,
                    'attachment': (
                    filename, open(path_to_attachment, 'rb'), 'file')}
        )
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token(),
            'keyManagerToken': self.bot_client.get_sym_auth().get_key_manager_token(),
            'Content-Type': data.content_type
        }
        response = requests.post(url, data=data, headers=headers,
                                 proxies=self.agent_proxies)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.send_msg(stream_id, msg)

        pass

    def get_msg_attachments(self, stream_id, msg_id, file_id):
        logging.debug('MessageClient/getAttachments()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token(),
            'keyManagerToken': self.bot_client.get_sym_auth().get_key_manager_token()
        }
        url = self.config.data['agentHost'] + \
              '/agent/v1/stream/{0}/attachment?msg_id={1}&file_id={2}'\
                  .format(stream_id, msg_id, file_id)
        response = requests.get(url, headers=headers, proxies=self.agent_proxies)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_msg_attachments(stream_id, msg_id, file_id)

    # go on admin clients --> Contains sample data just for example's sake
    def import_message(self):
        logging.debug('MessageClient/import_message()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token(),
            'keyManagerToken': self.bot_client.get_sym_auth().get_key_manager_token()
        }
        url = self.config.data['agentHost']+'/agent/v4/message/import'
        payload = {
            "message": "<messageML>Imported message</messageML>",
            "format": "MESSAGEML",
            "intendedMessageTimestamp": 1433045622000,
            "intendedMessageFromUserId": 7215545057281,
            "originatingSystemId": "",
            "originalMessageId": "",
            "streamId": ""
        }
        response = requests.post(
            url, headers=headers,
            data=payload, proxies=self.agent_proxies
        )
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.import_message()

    # go on admin clients
    def suppress_message(self, id):
        logging.debug('MessageClient/suppress_message()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token(),
            'keyManagerToken': self.bot_client.get_sym_auth().get_key_manager_token()
        }
        url = self.config.data['podHost'] + \
              '/pod/v1/admin/messagesuppression/{0}/suppress'.format(id)
        response = requests.post(url, headers=headers, proxies=self.pod_proxies)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.suppress_message(id)

    def post_msg_search(self):
        logging.debug('MessageClient/post_msg_search()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token(),
            'keyManagerToken': self.bot_client.get_sym_auth().get_key_manager_token()
        }
        url = self.config.data['agentHost']+'/agent/v1/message/search'
        payload = {
            'hashtag': 'reed'
        }
        response = requests.post(
            url, headers=headers,
            json=payload, proxies=self.agent_proxies
        )
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.post_msg_search(id)

    # contains sample query for example
    def get_msg_search(self):
        logging.debug('MessageClient/get_msg_search()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token(),
            'keyManagerToken': self.bot_client.get_sym_auth().get_key_manager_token()
        }
        url = self.config.data['agentHost']+'/agent/v1/message/search'
        query = {
            'query': 'hashtag:reed'
        }
        response = requests.get(url, headers=headers,
                                params=query, proxies=self.agent_proxies)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_msg_search(id)

    def get_msg_status(self, msg_id):
        logging.debug('MessageClient/get_msg_status()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + '/pod/v1/message/{0}/status'\
            .format(msg_id)
        response = requests.get(url, headers=headers, proxies=self.pod_proxies)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_msg_status(msg_id)

    def get_supported_attachment_types(self):
        logging.debug('MessageClient/getAttachmentTypes()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost']+'/pod/v1/files/allowedTypes'
        response = requests.get(url, headers=headers, proxies=self.pod_proxies)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            logging.debug('200')
            return json.loads(response.text)
        else:
            logging.debug(response.status_code)
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_supported_attachment_types()
