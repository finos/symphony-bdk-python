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

    def create_im(self, users_array):
        logging.debug('StreamClient/create_im()')
        url = '/pod/v1/im/create'
        return self.bot_client.execute_rest_call("POST", url, json=users_array)

    def create_im_admin(self, users_array):
        logging.debug('StreamClient/create_im_admin()')
        url = '/pod/v1/admin/im/create'
        return self.bot_client.execute_rest_call("POST", url, json=users_array)

    # contains sample data for example's sake
    def create_room(self):
        logging.debug('StreamClient/create_room()')
        url = '/pod/v3/room/create'
        data = {
            "name": "butlahsroom",
            "description": "meant for testing with butler"
        }
        return self.bot_client.execute_rest_call("POST", url, json=data)

    # contains example data dictionary for example sake
    def update_room(self, stream_id):
        logging.debug('StreamClient/update_room()')
        url = '/pod/v3/room/{0}/update'.format(stream_id)
        data = {
            "name": "updatedRoomName"
        }
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def get_room_info(self, stream_id):
        logging.debug('StreamClient/roomInfo()')
        url = '/pod/v3/room/{0}/info'.format(stream_id)
        return self.bot_client.execute_rest_call('GET', url)

    def activate_room(self, stream_id, active=True):
        logging.debug('StreamClient/activate_room()')
        url = '/pod/v1/room/{0}/setActive?active={1}'.format(stream_id, active)
        return self.bot_client.execute_rest_call('POST', url)

    def deactivate_room(self, stream_id, active=False):
        logging.debug('StreamClient/activate_room()')
        url = '/pod/v1/room/{0}/setActive?active={1}'.format(stream_id, active)
        return self.bot_client.execute_rest_call('POST', url)

    def get_room_members(self, stream_id):
        logging.debug('StreamClient/get_room_members()')
        url = '/pod/v2/room/{0}/membership/list'.format(stream_id)
        return self.bot_client.execute_rest_call('GET', url)

    def add_member_to_room(self, stream_id, user_id):
        logging.debug('StreamClient/addMember()')
        url = '/pod/v1/room/{0}/membership/add'.format(stream_id)
        data = {'id': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    # contains sample data dictionary for example --> see documentation for
    # further detail
    def share_room(self, stream_id):
        logging.debug('StreamClient/share_room()')
        url = '/agent/v3/stream/{0}/share'.format(stream_id)
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
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def remove_member_from_room(self, stream_id, user_id):
        logging.debug('StreamClient/removeMember()')
        url = '/pod/v1/room/{0}/membership/remove'.format(stream_id)
        data = {'id': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def promote_user_to_owner(self, stream_id, user_id):
        logging.debug('StreamClient/promoteOwner()')
        url = '/pod/v1/room/{0}/membership/promoteOwner'.format(stream_id)
        data = {'id': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def demote_user_from_owner(self, stream_id, user_id):
        logging.debug('StreamClient/demoteOwner()')
        url = '/pod/v1/room/{0}/membership/demoteOwner'.format(stream_id)
        data = {'id': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def search_rooms(self, skip=0, limit=50):
        logging.debug('StreamClient/roomSearch()')
        url = '/pod/v3/room/search'
        params = {'skip': skip, 'limit':limit}
        data = {'query': 'butlahsroom'}
        return self.bot_client.execute_rest_call('POST', url, params=params, json=data)

    def get_user_streams(self, skip=0, limit=50):
        logging.debug('StreamClient/listUserStreams()')
        url = '/pod/v1/streams/list'
        data = {
            "streamTypes": [
                {"type": "IM"},
                {"type": "MIM"},
                {"type": "ROOM"},
                {"type": "POST"}
            ],
            "includeInactiveStreams": True
        }
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def stream_info_v2(self, stream_id):
        logging.debug('StreamClient/stream_info_v2()')
        url = '/pod/v2/streams/{0}/info'.format(stream_id)
        return self.bot_client.execute_rest_call('GET', url)

    def list_streams_enterprise(self, skip=0, limit=50):
        logging.debug('StreamClient/list_streams_enterprise()')
        url = '/pod/v1/admin/streams/list'
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
        return self.bot_client.execute_rest_call('POST', url, params=params, json=data)

    def list_streams_enterprise_v2(self, skip=0, limit=50):
        logging.debug('StreamClient/list_streams_enterprise_v2()')
        url = '/pod/v2/admin/streams/list'
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
        return self.bot_client.execute_rest_call('POST', url, params=params, json=data)

    def get_stream_members(self, stream_id, skip=0, limit=100):
        logging.debug('StreamClient/get_stream_members()')
        url = '/pod/v1/admin/stream/{0}/membership/list'.format(stream_id)
        return self.bot_client.execute_rest_call('POST', url)
