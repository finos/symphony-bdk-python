import logging

from .api_client import APIClient


# child class of APIClient --> Extends error handling functionality
# StreamClient class contains a series of functions corresponding to all stream
# endpoints on the REST API.


class StreamClient(APIClient):

    def __init__(self, bot_client):
        self.bot_client = bot_client

    def create_im(self, users_array):
        """
        Creates a new single or multi-party instant message conversation or returns
        an existing IM or MIM between the specified users and the calling user.
        """
        logging.debug('StreamClient/create_im()')
        url = '/pod/v1/im/create'
        return self.bot_client.execute_rest_call("POST", url, json=users_array)

    def create_im_admin(self, users_array):
        """
        Creates a new single or multi-party instant message conversation or returns
        an existing IM or MIM between the specified users, but excludes the calling user.
        """
        logging.debug('StreamClient/create_im_admin()')
        url = '/pod/v1/admin/im/create'
        return self.bot_client.execute_rest_call("POST", url, json=users_array)

    def create_room(self, roomToCreate):
        """
        Creates a new chatroom. See Room Attributes for room creation parameters.
        Example Room Object. All required

        roomToCreate = {
            "name": (string) Room name,
            "description": (string) Room description,
            "keywords": [
                {"key": "key1", "value": "value1"},
                {"key": "key2", "value": "value2"}
                ...
            ],
            "membersCanInvite": (bool) If true, any chat room participant can add new participants. If false, only owners can add new participants,
            "discoverable": (bool) If true, this chat room (name, description and messages) non-participants can search for this room. If false, only participants can search for this room,
            "public": (bool) If true, this is a public chatroom. If false, a private chatroom. Note: Once this value is set for a room, it is read-only and can’t be updated,
            "readOnly": (bool) If true, only stream owners can send messages. Once this value is set for a room, it is read-only and can’t be updated,
            "copyProtected": (bool) If true, users cannot copy content from this room. Once this value is set to true for a room, it is read-only and can’t be updated,
            "crossPod": (bool) If true, this room is a cross-pod room,
            "viewHistory": (bool) If true, new members can view the room chat history of the room,
            "multiLateralRoom": (bool) If true, this is a multilateral room where users belonging to more than 2 companies can be found
        }
        """
        logging.debug('StreamClient/create_room()')
        url = '/pod/v3/room/create'
        return self.bot_client.execute_rest_call("POST", url, json=roomToCreate)

    def update_room(self, stream_id, **kwargs):
        """
        Updates the attributes of an existing chat room.
        Pass in room_obj like such:

        room_obj = {
            "name" : "updated room",
            "description": "testing update room function",
        }

        update_room(stream_id, **room_obj)
        """
        logging.debug('StreamClient/update_room()')
        url = '/pod/v3/room/{0}/update'.format(stream_id)
        return self.bot_client.execute_rest_call('POST', url, json=kwargs)

    def get_room_info(self, stream_id):
        """
        Returns information about a particular chat room.
        """
        logging.debug('StreamClient/get_room_info()')
        url = '/pod/v3/room/{0}/info'.format(stream_id)
        return self.bot_client.execute_rest_call('GET', url)

    def activate_room(self, stream_id):
        """
        Deactivate or reactivate a chatroom. At creation, a new chatroom is active.
        """
        logging.debug('StreamClient/activate_room()')
        url = '/pod/v1/room/{0}/setActive'.format(stream_id)
        params = {
            'active': True
        }
        return self.bot_client.execute_rest_call('POST', url, params=params)

    def deactivate_room(self, stream_id):
        """
        Deactivate or reactivate a chatroom. At creation, a new chatroom is active.
        """
        logging.debug('StreamClient/activate_room()')
        url = '/pod/v1/room/{0}/setActive'.format(stream_id)
        params = {
            'active': False
        }
        return self.bot_client.execute_rest_call('POST', url, params=params)

    def get_room_members(self, stream_id):
        """
        Lists the current members of an existing room.
        """
        logging.debug('StreamClient/get_room_members()')
        url = '/pod/v2/room/{0}/membership/list'.format(stream_id)
        return self.bot_client.execute_rest_call('GET', url)

    def add_member_to_room(self, stream_id, user_id):
        """
        Adds a new member to an existing room.
        """
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
        """
        Share third-party content, such as a news article, into the specified stream.
        The stream can be a chat room, an IM, or an MIM.
        content: An object containing the fields required for defining an article

        content = {
            "articleId": (string) A unique ID for this article, not used by any other article,
            "title": (string) The title of the article,
            "subTitle": (string) The subtitle of the article
            "description": (string) The description of the article,
            "message" : (string) The message text that can be sent along with the shared article,
            "publisher": (string)* Publisher of the article,
            "publishDate": (string) Article publish date in unix timestamp,
            "thumbnailUrl": (string) URL to the thumbnail image,
            "author": (string)* Author of the article,
            "articleUrl": (string) URL to the article,
            "summary": (string) Preview summary of the article,
            "appId": (string)* App ID of the calling application,
            "appName": (string) App name of the calling application,
            "appIconUrl": (string) App icon URL of the calling application
        }
        """
        logging.debug('StreamClient/share_room()')
        url = '/agent/v3/stream/{0}/share'.format(stream_id)
        data = {
            "type": "com.symphony.sharing.article",
            "content": content
        }
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def remove_member_from_room(self, stream_id, user_id):
        """
        Removes an existing member from an existing room
        """
        logging.debug('StreamClient/remove_member_from_room()')
        url = '/pod/v1/room/{0}/membership/remove'.format(stream_id)
        data = {'id': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def promote_user_to_owner(self, stream_id, user_id):
        """
        Promotes user to owner of the chat room.
        """
        logging.debug('StreamClient/promote_user_to_owner()')
        url = '/pod/v1/room/{0}/membership/promoteOwner'.format(stream_id)
        data = {'id': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def demote_user_from_owner(self, stream_id, user_id):
        """
        Demotes room owner to a participant in the chat room.
        """
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
        """
        Search for rooms, querying name, description, and specified keywords.

        search_rooms('query', labels = ['hack', 'test', 'room'], active = True)
        """
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
        """
        Returns a list of all the streams of which the requesting user is a member,
        sorted by creation date (ascending - oldest to newest).
        """
        logging.debug('StreamClient/get_user_streams()')
        url = '/pod/v1/streams/list'
        if (stream_types == 'ALL'):
            stream_types = [
                    {"type": "IM"},
                    {"type": "MIM"},
                    {"type": "ROOM"},
                    {"type": "POST"}
                ]
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
        """
        Returns information about a particular stream.
        """
        logging.debug('StreamClient/stream_info_v2()')
        url = '/pod/v2/streams/{0}/info'.format(stream_id)
        return self.bot_client.execute_rest_call('GET', url)


    def list_streams_enterprise(self, skip=0, limit=50, **kwargs):
        """
        Returns a list of all the streams (IMs, MIMs, and chatrooms) for the calling
        user's company, sorted by creation date (ascending – oldest to newest).
        Filtering parameters can be used to narrow the list of streams that are returned.

        Required Permissions: This endpoint may only be called by Service User accounts with the User Provisioning role.

        Available kwargs:

        streamTypes: A list of stream types that will be returned (IM, MIM, ROOM). If not specified, streams of all types are returned.
        scope: The scope of the stream: INTERNAL (restricted to members of the calling user's company) or EXTERNAL (including members of the calling user's company, as well as another firm). If not specified, returns streams of either scope.
        origin: The origin of the room: INTERNAL (created by a user of the calling user's company) or EXTERNAL (created by a user of another company). If not specified, returns streams of either origin. Only applies to chatrooms with External scope.
        privacy: The privacy setting of the room: PRIVATE (members must be added) OR PUBLIC (anyone can join). If not specified, returns both private and public rooms. Only applies to chatrooms with internal scope.
        status: The status of the room: ACTIVE or INACTIVE. If not specified, both active and inactive streams are returned.
        startDate: Restricts result set to rooms that have been modified since this date (an Epoch timestamp specified in milliseconds). When specified along with endDate, enables the developer to specify rooms modified within a given time range.
        endDate: Restricts result set to rooms that have been modified prior to this date (an Epoch timestamp specified in milliseconds). When specified along with startDate, enables the developer to specify rooms modified within a given time range.
        """
        logging.debug('StreamClient/list_streams_enterprise()')
        url = '/pod/v1/admin/streams/list'
        params = {
            'skip': skip,
            'limit': limit
        }
        return self.bot_client.execute_rest_call('POST', url, params=params, json=kwargs)

    def list_streams_enterprise_v2(self, skip=0, limit=50, **kwargs):
        """
        Returns a list of all the streams (IMs, MIMs, and chatrooms) for the calling
        user's company, sorted by creation date (ascending – oldest to newest).
        Filtering parameters can be used to narrow the list of streams that are returned.

        Required Permissions: This endpoint may only be called by Service User accounts with the User Provisioning role.

        Available kwargs:

        streamTypes: A list of stream types that will be returned (IM, MIM, ROOM). If not specified, streams of all types are returned.
        scope: The scope of the stream: INTERNAL (restricted to members of the calling user's company) or EXTERNAL (including members of the calling user's company, as well as another firm). If not specified, returns streams of either scope.
        origin: The origin of the room: INTERNAL (created by a user of the calling user's company) or EXTERNAL (created by a user of another company). If not specified, returns streams of either origin. Only applies to chatrooms with External scope.
        privacy: The privacy setting of the room: PRIVATE (members must be added) OR PUBLIC (anyone can join). If not specified, returns both private and public rooms. Only applies to chatrooms with internal scope.
        status: The status of the room: ACTIVE or INACTIVE. If not specified, both active and inactive streams are returned.
        startDate: Restricts result set to rooms that have been modified since this date (an Epoch timestamp specified in milliseconds). When specified along with endDate, enables the developer to specify rooms modified within a given time range.
        endDate: Restricts result set to rooms that have been modified prior to this date (an Epoch timestamp specified in milliseconds). When specified along with startDate, enables the developer to specify rooms modified within a given time range.
        """
        logging.debug('StreamClient/list_streams_enterprise_v2()')
        url = '/pod/v2/admin/streams/list'
        params = {
            'skip': skip,
            'limit': limit
        }
        return self.bot_client.execute_rest_call('POST', url, params=params, json=kwargs)

    def get_stream_members(self, stream_id, skip=0, limit=100):
        """
        Returns a list of all the current members of a stream (IM, MIM, or chatroom
        Required Permissions:

        To get the stream membership of any stream in your enterprise, you should
        call this endpoint with a Service User account with the User Provisioning role.
        The Service User does not need to be a member of the stream.
        See Permissions for a list of roles and associated privileges.
        """
        logging.debug('StreamClient/get_stream_members()')
        url = '/pod/v1/admin/stream/{0}/membership/list'.format(stream_id)
        params = {
            'skip': skip,
            'limit': limit
        }
        return self.bot_client.execute_rest_call('GET', url, params=params)
