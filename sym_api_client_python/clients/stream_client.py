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

    # Example Room Object. All required
    # '{
    #     "name": (string) Room name,
    #     "description": (string) Room description,
    #     "keywords": [
    #         {"key": "key1", "value": "value1"},
    #         {"key": "key2", "value": "value2"}
    #         ...
    #     ],
    #     "membersCanInvite": (bool) If true, any chat room participant can add new participants. If false, only owners can add new participants,
    #     "discoverable": (bool) If true, this chat room (name, description and messages) non-participants can search for this room. If false, only participants can search for this room,
    #     "public": (bool) If true, this is a public chatroom. If false, a private chatroom. Note: Once this value is set for a room, it is read-only and can’t be updated,
    #     "readOnly": (bool) If true, only stream owners can send messages. Once this value is set for a room, it is read-only and can’t be updated,
    #     "copyProtected": (bool) If true, users cannot copy content from this room. Once this value is set to true for a room, it is read-only and can’t be updated,
    #     "crossPod": (bool) If true, this room is a cross-pod room,
    #     "viewHistory": (bool) If true, new members can view the room chat history of the room,
    #     "multiLateralRoom": (bool) If true, this is a multilateral room where users belonging to more than 2 companies can be found
    # }'
    def create_room(self, roomToCreate):
        logging.debug('StreamClient/create_room()')
        url = '/pod/v3/room/create'
        return self.bot_client.execute_rest_call("POST", url, json=roomToCreate)

    # Pass attributes you want to update into **kwargs
    def update_room(self, stream_id, **kwargs):
        logging.debug('StreamClient/update_room()')
        url = '/pod/v3/room/{0}/update'.format(stream_id)
        return self.bot_client.execute_rest_call('POST', url, json=kwargs)

    def get_room_info(self, stream_id):
        logging.debug('StreamClient/get_room_info()')
        url = '/pod/v3/room/{0}/info'.format(stream_id)
        return self.bot_client.execute_rest_call('GET', url)

    def activate_room(self, stream_id):
        logging.debug('StreamClient/activate_room()')
        url = '/pod/v1/room/{0}/setActive'.format(stream_id)
        params = {
            'active': True
        }
        return self.bot_client.execute_rest_call('POST', url, params=params)

    def deactivate_room(self, stream_id):
        logging.debug('StreamClient/activate_room()')
        url = '/pod/v1/room/{0}/setActive'.format(stream_id)
        params = {
            'active': False
        }
        return self.bot_client.execute_rest_call('POST', url, params=params)

    def get_room_members(self, stream_id):
        logging.debug('StreamClient/get_room_members()')
        url = '/pod/v2/room/{0}/membership/list'.format(stream_id)
        return self.bot_client.execute_rest_call('GET', url)

    def add_member_to_room(self, stream_id, user_id):
        logging.debug('StreamClient/add_member_to_room()')
        url = '/pod/v1/room/{0}/membership/add'.format(stream_id)
        data = {'id': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    # Content Object. * is required. Either articleId or articleUrl must be specified
    # "content":{
    #     "articleId": (string) A unique ID for this article, not used by any other article,
    #     "title": (string) The title of the article,
    #     "subTitle": (string) The subtitle of the article
    #     "description": (string) The description of the article,
    #     "message" : (string) The message text that can be sent along with the shared article,
    #     "publisher": (string)* Publisher of the article,
    #     "publishDate": (string) Article publish date in unix timestamp,
    #     "thumbnailUrl": (string) URL to the thumbnail image,
    #     "author": (string)* Author of the article,
    #     "articleUrl": (string) URL to the article,
    #     "summary": (string) Preview summary of the article,
    #     "appId": (string)* App ID of the calling application,
    #     "appName": (string) App name of the calling application,
    #     "appIconUrl": (string) App icon URL of the calling application
    # }
    def share_room(self, stream_id, content):
        logging.debug('StreamClient/share_room()')
        url = '/agent/v3/stream/{0}/share'.format(stream_id)
        data = {
            "type": "com.symphony.sharing.article",
            "content": content
        }
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def remove_member_from_room(self, stream_id, user_id):
        logging.debug('StreamClient/remove_member_from_room()')
        url = '/pod/v1/room/{0}/membership/remove'.format(stream_id)
        data = {'id': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def promote_user_to_owner(self, stream_id, user_id):
        logging.debug('StreamClient/promote_user_to_owner()')
        url = '/pod/v1/room/{0}/membership/promoteOwner'.format(stream_id)
        data = {'id': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def demote_user_from_owner(self, stream_id, user_id):
        logging.debug('StreamClient/demote_user_from_owner()')
        url = '/pod/v1/room/{0}/membership/demoteOwner'.format(stream_id)
        data = {'id': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    # Available kwargs:
    # labels: A list of room keywords whose values will be queried.
    # active: If true, restricts the search to active rooms. If false, restricts the search to inactive rooms. If not specified, includes both active and inactive rooms.
    # private: If true, includes public and private rooms in the search results. If false or unspecified only public rooms are returned.
    # creator: If provided, restricts the search to rooms created by the specified user.
    # owner: If provided, restricts the search to rooms owned by the specified user.
    # member: If provided, restricts the search to rooms where the specified user is a member.
    # sortOrder: Sort algorithm to be used. Supports two values: BASIC (legacy algorithm) and RELEVANCE (enhanced algorithm).
    def search_rooms(self, query, skip=0, limit=50, **kwargs):
        logging.debug('StreamClient/search_rooms()')
        url = '/pod/v3/room/search'
        params = {
            'skip': skip,
            'limit':limit
        }
        data = {
            'query': query
        }
        data.update(kwargs)
        return self.bot_client.execute_rest_call('POST', url, params=params, json=data)

    def get_user_streams(self, skip=0, limit=50, stream_types = 'ALL', include_inactive = True):
        logging.debug('StreamClient/get_user_streams()')
        url = '/pod/v1/streams/list'
        if (stream_types == 'ALL'):
            stream_types = {
                "streamTypes": [
                    {"type": "IM"},
                    {"type": "MIM"},
                    {"type": "ROOM"},
                    {"type": "POST"}
                ],
            }
        data = {
            'streamTypes': stream_types,
            'includeInactiveStreams': include_inactive
        }
        params = {
            'skip': skip,
            'limit': limit
        }
        return self.bot_client.execute_rest_call('POST', url, json=data, params=params)

    def stream_info_v2(self, stream_id):
        logging.debug('StreamClient/stream_info_v2()')
        url = '/pod/v2/streams/{0}/info'.format(stream_id)
        return self.bot_client.execute_rest_call('GET', url)

    # Available kwargs:
    # streamTypes: A list of stream types that will be returned (IM, MIM, ROOM). If not specified, streams of all types are returned.
    # scope: The scope of the stream: INTERNAL (restricted to members of the calling user's company) or EXTERNAL (including members of the calling user's company, as well as another firm). If not specified, returns streams of either scope.
    # origin: The origin of the room: INTERNAL (created by a user of the calling user's company) or EXTERNAL (created by a user of another company). If not specified, returns streams of either origin. Only applies to chatrooms with External scope.
    # privacy: The privacy setting of the room: PRIVATE (members must be added) OR PUBLIC (anyone can join). If not specified, returns both private and public rooms. Only applies to chatrooms with internal scope.
    # status: The status of the room: ACTIVE or INACTIVE. If not specified, both active and inactive streams are returned.
    # startDate: Restricts result set to rooms that have been modified since this date (an Epoch timestamp specified in milliseconds). When specified along with endDate, enables the developer to specify rooms modified within a given time range.
    # endDate: Restricts result set to rooms that have been modified prior to this date (an Epoch timestamp specified in milliseconds). When specified along with startDate, enables the developer to specify rooms modified within a given time range.
    def list_streams_enterprise(self, skip=0, limit=50, **kwargs):
        logging.debug('StreamClient/list_streams_enterprise()')
        url = '/pod/v1/admin/streams/list'
        params = {
            'skip': skip,
            'limit': limit
        }
        return self.bot_client.execute_rest_call('POST', url, params=params, json=kwargs)

    # Available kwargs same as list_streams_enterprise
    def list_streams_enterprise_v2(self, skip=0, limit=50, **kwargs):
        logging.debug('StreamClient/list_streams_enterprise_v2()')
        url = '/pod/v2/admin/streams/list'
        params = {
            'skip': skip,
            'limit': limit
        }
        return self.bot_client.execute_rest_call('POST', url, params=params, json=kwargs)

    def get_stream_members(self, stream_id, skip=0, limit=100):
        logging.debug('StreamClient/get_stream_members()')
        url = '/pod/v1/admin/stream/{0}/membership/list'.format(stream_id)
        params = {
            'skip': skip,
            'limit': limit
        }
        return self.bot_client.execute_rest_call('POST', url, params=params)
