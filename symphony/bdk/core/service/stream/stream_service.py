from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.gen.agent_api.share_api import ShareApi
from symphony.bdk.gen.agent_model.share_content import ShareContent
from symphony.bdk.gen.agent_model.v2_message import V2Message
from symphony.bdk.gen.pod_api.room_membership_api import RoomMembershipApi
from symphony.bdk.gen.pod_api.streams_api import StreamsApi
from symphony.bdk.gen.pod_model.membership_list import MembershipList
from symphony.bdk.gen.pod_model.room_detail import RoomDetail
from symphony.bdk.gen.pod_model.stream import Stream
from symphony.bdk.gen.pod_model.stream_attributes import StreamAttributes
from symphony.bdk.gen.pod_model.stream_filter import StreamFilter
from symphony.bdk.gen.pod_model.stream_list import StreamList
from symphony.bdk.gen.pod_model.user_id import UserId
from symphony.bdk.gen.pod_model.user_id_list import UserIdList
from symphony.bdk.gen.pod_model.v2_admin_stream_filter import V2AdminStreamFilter
from symphony.bdk.gen.pod_model.v2_admin_stream_list import V2AdminStreamList
from symphony.bdk.gen.pod_model.v2_membership_list import V2MembershipList
from symphony.bdk.gen.pod_model.v2_room_search_criteria import V2RoomSearchCriteria
from symphony.bdk.gen.pod_model.v2_stream_attributes import V2StreamAttributes
from symphony.bdk.gen.pod_model.v3_room_attributes import V3RoomAttributes
from symphony.bdk.gen.pod_model.v3_room_detail import V3RoomDetail
from symphony.bdk.gen.pod_model.v3_room_search_results import V3RoomSearchResults


class StreamService:
    """Service class to manage streams.
    """

    def __init__(self, streams_api: StreamsApi, room_membership_api: RoomMembershipApi, share_api: ShareApi,
                 auth_session: AuthSession):
        """

        :param streams_api: a generated StreamsApi instance
        :param room_membership_api: a generated RoomMembershipApi instance
        :param share_api: a generated ShareApi instance
        :param auth_session: the bot session
        """
        self._streams_api = streams_api
        self._room_membership_api = room_membership_api
        self._share_api = share_api
        self._auth_session = auth_session

    async def get_stream(self, stream_id: str) -> V2StreamAttributes:
        """Wraps the `Stream Info V2 <https://developers.symphony.com/restapi/reference#stream-info-v2>`_ endpoint.

        :param stream_id: the ID of the stream to be retrieved
        :return: the information about the given stream
        """
        return await self._streams_api.v2_streams_sid_info_get(sid=stream_id,
                                                               session_token=await self._auth_session.session_token)

    async def list_streams(self, stream_filter: StreamFilter, skip: int = None,
                           limit: int = None) -> [StreamAttributes]:
        """Wraps the `List Streams <https://developers.symphony.com/restapi/reference#add-member>`_ endpoint.

        :param stream_filter: the stream searching criteria
        :param skip: number of stream results to skip, defaults to 0
        :param limit: maximum number of streams to return, defaults to 50
        :return: the list of stream retrieved matching the search filter
        """
        streams = self._streams_api.v1_streams_list_post(filter=stream_filter, skip=skip, limit=limit,
                                                         session_token=await self._auth_session.session_token)
        return await streams.value

    async def add_member_to_room(self, user_id: int, room_id: int):
        """Wraps the `Add Member <https://developers.symphony.com/restapi/reference#add-member>`_ endpoint.

        :param user_id: the id of the user to be added to the room
        :param room_id: the id of the room in which to add the user
        :return: None
        """
        await self._room_membership_api.v1_room_id_membership_add_post(
            payload=UserId(id=user_id), id=room_id,
            session_token=await self._auth_session.session_token)

    async def remove_member_from_room(self, user_id: int, room_id: int):
        """Wraps the `Remove Member <https://developers.symphony.com/restapi/reference#remove-member>`_ endpoint.

        :param user_id: the id of the user to be removed from the room
        :param room_id: the id of the room from which to remove the user
        :return: None
        """
        await self._room_membership_api.v1_room_id_membership_remove_post(
            payload=UserId(id=user_id), id=room_id,
            session_token=await self._auth_session.session_token)

    async def share(self, stream_id: str, content: ShareContent) -> V2Message:
        """Wraps the `Share <https://developers.symphony.com/restapi/reference#share-v3>`_ endpoint.

        :param stream_id: the id of the stream in which to share the given content
        :param content: the third-party content to be shared
        :return: the created message
        """
        return await self._share_api.v3_stream_sid_share_post(
            sid=stream_id, share_content=content, session_token=await self._auth_session.session_token,
            key_manager_token=await self._auth_session.key_manager_token)

    async def promote_user_to_room_owner(self, user_id: int, room_id: int):
        """Wraps the `Promote Owner <https://developers.symphony.com/restapi/reference#promote-owner>`_ endpoint.

        :param user_id: the id of the user to be promoted as owner
        :param room_id: the room id
        :return: None
        """
        await self._room_membership_api.v1_room_id_membership_promote_owner_post(
            id=room_id, payload=UserId(id=user_id), session_token=await self._auth_session.session_token)

    async def demote_owner_to_room_participant(self, user_id: int, room_id: int):
        """Wraps the `Demote Owner <https://developers.symphony.com/restapi/reference#demote-owner>`_ endpoint.

        :param user_id: the id of the room owner to be demoted
        :param room_id: the room id
        :return:
        """
        await self._room_membership_api.v1_room_id_membership_demote_owner_post(
            id=room_id, payload=UserId(id=user_id), session_token=await self._auth_session.session_token)

    async def create(self, user_ids: [int]) -> Stream:
        """Wraps the `Create IM or MIM <https://developers.symphony.com/restapi/reference#create-im-or-mim>`_ endpoint.

        Create a new single or multi party instant message conversation between the caller and specified users.
        The caller is implicitly included in the members of the created chat.
        Duplicate users will be included in the membership of the chat but the duplication will be silently ignored.
        If there is an existing IM conversation with the same set of participants then the id of that existing stream
        will be returned.
        If the given list of user ids contains only one id, an IM will be created, otherwise, a MIM will be created.

        :param user_ids: the list of user ids ti be put as room participants.
        :return: the created stream
        """
        return await self._streams_api.v1_im_create_post(uid_list=UserIdList(value=user_ids),
                                                         session_token=await self._auth_session.session_token)

    async def create(self, room_attributes: V3RoomAttributes) -> V3RoomDetail:
        """

        :param room_attributes:
        :return:
        """
        return await self._streams_api.v3_room_create_post(payload=room_attributes,
                                                           session_token=await self._auth_session.session_token)

    async def search_rooms(self, query: V2RoomSearchCriteria, skip: int = None,
                           limit: int = None) -> V3RoomSearchResults:
        """

        :param query:
        :param skip:
        :param limit:
        :return:
        """
        return await self._streams_api.v3_room_search_post(query=query, skip=skip, limit=limit,
                                                           session_token=await self._auth_session.session_token)

    async def get_room_info(self, room_id: str) -> V3RoomDetail:
        """

        :param room_id:
        :return:
        """
        return await self._streams_api.v3_room_id_info_get(id=room_id,
                                                           session_token=await self._auth_session.session_token)

    async def set_room_active(self, room_id: str, active: bool) -> RoomDetail:
        """

        :param room_id:
        :param active:
        :return:
        """
        return await self._streams_api.v1_room_id_set_active_post(id=room_id, active=active,
                                                                  session_token=await self._auth_session.session_token)

    async def update_room(self, room_id: str, room_attributes: V3RoomAttributes) -> V3RoomDetail:
        """

        :param room_id:
        :param room_attributes:
        :return:
        """
        return await self._streams_api.v3_room_id_update_post(id=room_id, payload=room_attributes,
                                                              session_token=await self._auth_session.session_token)

    async def create_im_admin(self, user_ids: [int]) -> str:
        """

        :param user_ids:
        :return:
        """
        stream = await self._streams_api.v1_admin_im_create_post(uid_list=UserIdList(value=user_ids),
                                                                 session_token=await self._auth_session.session_token)
        return stream.id

    async def set_room_active_admin(self, room_id: str, active: bool) -> RoomDetail:
        """

        :param room_id:
        :param active:
        :return:
        """
        return await self._streams_api.v1_admin_room_id_set_active_post(
            id=room_id, active=active,
            session_token=await self._auth_session.session_token)

    async def list_streams_admin(self, stream_filter: V2AdminStreamFilter, skip: int = None,
                                 limit: int = None) -> V2AdminStreamList:
        """

        :param stream_filter:
        :param skip:
        :param limit:
        :return:
        """
        return await self._streams_api.v2_admin_streams_list_post(filter=stream_filter, skip=skip, limit=limit,
                                                                  session_token=await self._auth_session.session_token)

    async def list_stream_members(self, stream_id: str, skip: int = None, limit: int = None) -> V2MembershipList:
        """

        :param stream_id:
        :param skip:
        :param limit:
        :return:
        """
        return await self._streams_api.v1_admin_stream_id_membership_list_get(
            id=stream_id, skip=skip, limit=limit,
            session_token=await self._auth_session.session_token)

    async def list_room_members(self, room_id: str) -> MembershipList:
        """

        :param room_id:
        :return:
        """
        return await self._room_membership_api.v2_room_id_membership_list_get(
            id=room_id,
            session_token=await self._auth_session.session_token)
