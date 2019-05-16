import requests
import json
import logging
from .api_client import APIClient
from ..exceptions.UnauthorizedException import UnauthorizedException

# child class of APIClient --> Extends error handling functionality
# StreamClient class contains a series of functions corresponding to all stream
# endpoints on the REST API.


class StreamClient(APIClient):

    def __init__(self, bot_client):
        self.bot_client = bot_client
        self.config = self.bot_client.get_sym_config()
        self.pod_proxies = self.config.data['podProxyRequestObject']

    def create_im(self, users_array):
        logging.debug('StreamClient/create_im()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost']+'/pod/v1/im/create'
        response = requests.post(
            url, json=users_array, headers=headers, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.create_im(users_array)

    def create_im_admin(self, users_array):
        logging.debug('StreamClient/create_im_admin()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost']+'/pod/v1/admin/im/create'
        response = requests.post(
            url, json=users_array, headers=headers, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.create_im_admin(users_array)

    # contains sample data for example's sake
    def create_room(self):
        logging.debug('StreamClient/create_room()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost']+'/pod/v3/room/create'
        data = {
            "name": "butlahsroom",
            "description": "meant for testing with butler"
        }
        response = requests.post(
            url, headers=headers, json=data, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.create_room()

    # contains example data dictionary for example sake
    def update_room(self, stream_id):
        logging.debug('StreamClient/update_room()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + \
              '/pod/v3/room/{0}/update'.format(stream_id)
        data = {
            "name": "updatedRoomName"
        }
        response = requests.post(
            url, headers=headers, json=data, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.update_room(stream_id)

    def get_room_info(self, stream_id):
        logging.debug('StreamClient/roomInfo()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + \
              '/pod/v3/room/{0}/info'.format(stream_id)
        response = requests.get(
            url, headers=headers, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_room_info(stream_id)

    def activate_room(self, stream_id, active=True):
        logging.debug('StreamClient/activate_room()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + \
              '/pod/v1/room/{0}/setActive?active={1}'.format(stream_id, active)
        response = requests.post(
            url, headers=headers, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.activate_room(stream_id, active=True)

    def deactivate_room(self, stream_id, active=False):
        logging.debug('StreamClient/deactivate_room()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + \
              '/pod/v1/room/{0}/setActive?active={1}'.format(stream_id, active)
        response = requests.post(
            url, headers=headers, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.deactivate_room(stream_id, active=False)

    def get_room_members(self, stream_id):
        logging.debug('StreamClient/get_room_members()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + \
              '/pod/v2/room/{0}/membership/list'.format(stream_id)
        response = requests.get(
            url, headers=headers, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_room_members()

    def add_member_to_room(self, stream_id, user_id):
        logging.debug('StreamClient/addMember()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + \
              '/pod/v1/room/{0}/membership/add'.format(stream_id)
        data = {'id': user_id}
        response = requests.post(
            url, headers=headers, json=data, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.add_member_to_room(stream_id, user_id)

    # contains sample data dictionary for example --> see documentation for
    # further detail
    def share_room(self, stream_id):
        logging.debug('StreamClient/share_room()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token(),
            'keyManagerToken': self.bot_client.get_sym_auth().get_key_manager_token()
        }
        url = self.config.data['agentHost'] + \
              '/agent/v3/stream/{0}/share'.format(stream_id)
        data = {
            "type": "com.symphony.sharing.article",
            "content":{
                "articleId": "tsla",
                "title": "The Secrets Out: Tesla Enters China and Is Winning",
                "description": "Check this out",
                "publisher": "Capital Market Laboratories",
                "thumbnailUrl": "http://www.cmlviz.com/cmld3b/images/tesla-supercharger-stop.jpg",
                "author": "OPHIRGOTTLIEB",
                "articleUrl": "http://ophirgottlieb.tumblr.com/post/146623530819/the-secrets-out-tesla-enters-china-and-is",
                "summary": "Tesla Motors Inc. (NASDAQ:TSLA) has a CEO more famous than the firm itself, perhaps. Elon Musk has made some bold predictions, first stating that the firm would grow sales from 50,000 units in 2015 to 500,000 by 2020 powered by the less expensive Model 3 and the massive manufacturing capability of the Gigafactory.",
                "appId": "ticker",
                "appName": "Market Data Demo",
                "appIconUrl": "https://apps-dev.symphony.com/ticker/assets/images/logo.png"
            }
        }
        response = requests.post(
            url, headers=headers, json=data
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.share_room(stream_id)

    def remove_member_from_room(self, stream_id, user_id):
        logging.debug('StreamClient/removeMember()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + \
              '/pod/v1/room/{0}/membership/remove'.format(stream_id)
        data = {'id': user_id}
        response = requests.post(
            url, headers=headers, json=data, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.remove_member_from_room(stream_id, user_id)

    def promote_user_to_owner(self, stream_id, user_id):
        logging.debug('StreamClient/promoteOwner()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + \
              '/pod/v1/room/{0}/membership/promoteOwner'.format(stream_id)
        data = {'id': user_id}
        response = requests.post(
            url, headers=headers, json=data, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.promote_user_to_owner(stream_id, user_id)

    def demote_user_from_owner(self, stream_id, user_id):
        logging.debug('StreamClient/demoteOwner()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + \
              '/pod/v1/room/{0}/membership/demoteOwner'.format(stream_id)
        data = {'id': user_id}
        response = requests.post(
            url, headers=headers, json=data, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.demote_user_from_owner(stream_id, user_id)

    def search_rooms(self, skip=0, limit=50):
        logging.debug('StreamClient/roomSearch()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost']+'/pod/v3/room/search'
        params = {'skip': skip, 'limit':limit}
        data = {'query': 'butlahsroom'}
        response = requests.post(
            url, headers=headers, params=params, json=data,
            proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.search_rooms(skip=0, limit=50)

    def get_user_streams(self, skip=0, limit=50):
        logging.debug('StreamClient/listUserStreams()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost']+'/pod/v1/streams/list'
        data = {
            "streamTypes": [
                {"type": "IM"},
                {"type": "MIM"},
                {"type": "ROOM"},
                {"type": "POST"}
            ],
            "includeInactiveStreams": True
        }
        response = requests.post(
            url, headers=headers, json=data, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_user_streams(skip=0, limit=50)

    def stream_info_v2(self, stream_id):
        logging.debug('StreamClient/stream_info_v2()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + \
              '/pod/v2/streams/{0}/info'.format(stream_id)
        response = requests.get(
            url, headers=headers, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.stream_info_v2()

    def list_streams_enterprise(self, skip=0, limit=50):
        logging.debug('StreamClient/list_streams_enterprise()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + '/pod/v1/admin/streams/list'
        params = {'skip': skip, 'limit': limit}
        data = {
              "streamTypes": [{"type": "ROOM"}],
              "scope": "EXTERNAL",
              "origin": "EXTERNAL",
              "privacy": "PRIVATE",
              "status": "ACTIVE",
              "startDate": 1481575056047,
              "endDate": 1483038089833
        }
        response = requests.post(
            url, headers=headers, params=params, json=data,
            proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.list_streams_enterprise()

    def list_streams_enterprise_v2(self, skip=0, limit=50):
        logging.debug('StreamClient/list_streams_enterprise_v2()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + '/pod/v2/admin/streams/list'
        params = {'skip': skip, 'limit': limit}
        data = {
              "streamTypes": [{"type": "ROOM"}],
              "scope": "EXTERNAL",
              "origin": "EXTERNAL",
              "privacy": "PRIVATE",
              "status": "ACTIVE",
              "startDate": 1481575056047,
              "endDate": 1483038089833
        }
        response = requests.post(
            url, headers=headers, params=params, json=data,
            proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.list_streams_enterprise_v2()

    def get_stream_members(self, stream_id, skip=0, limit=100):
        logging.debug('StreamClient/get_stream_members()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost'] + \
              '/pod/v1/admin/stream/{0}/membership/list'.format(stream_id)
        response = requests.post(
            url, headers=headers, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_stream_members(stream_id)
