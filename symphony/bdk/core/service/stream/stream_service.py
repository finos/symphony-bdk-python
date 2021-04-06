from typing import AsyncGenerator

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.pagination import offset_based_pagination
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
from symphony.bdk.gen.pod_model.v2_admin_stream_info import V2AdminStreamInfo
from symphony.bdk.gen.pod_model.v2_admin_stream_list import V2AdminStreamList
from symphony.bdk.gen.pod_model.v2_member_info import V2MemberInfo
from symphony.bdk.gen.pod_model.v2_membership_list import V2MembershipList
from symphony.bdk.gen.pod_model.v2_room_search_criteria import V2RoomSearchCriteria
from symphony.bdk.gen.pod_model.v2_stream_attributes import V2StreamAttributes
from symphony.bdk.gen.pod_model.v3_room_attributes import V3RoomAttributes
from symphony.bdk.gen.pod_model.v3_room_detail import V3RoomDetail
from symphony.bdk.gen.pod_model.v3_room_search_results import V3RoomSearchResults


class OboStreamService:
    """Class exposing OBO-enabled endpoints for stream management."""

    def __init__(self, streams_api: StreamsApi, room_membership_api: RoomMembershipApi, share_api: ShareApi,
                 auth_session: AuthSession):
        """

        :param streams_api: a generated StreamsApi instance.
        :param room_membership_api: a generated RoomMembershipApi instance.
        :param share_api: a generated ShareApi instance.
        :param auth_session: the bot session.
        """
        self._streams_api = streams_api
        self._room_membership_api = room_membership_api
        self._share_api = share_api
        self._auth_session = auth_session

    async def get_stream(self, stream_id: str) -> V2StreamAttributes:
        """Returns information about a particular stream.
        Wraps the `Stream Info V2 <https://developers.symphony.com/restapi/reference#stream-info-v2>`_ endpoint.

        :param stream_id: the ID of the stream to be retrieved.
        :return: the information about the given stream.
        """
        return await self._streams_api.v2_streams_sid_info_get(sid=stream_id,
                                                               session_token=await self._auth_session.session_token)

    async def list_streams(self, stream_filter: StreamFilter, skip: int = 0,
                           limit: int = 50) -> StreamList:
        """Returns a list of all the streams of which the requesting user is a member,
        sorted by creation date (ascending - oldest to newest).
        Wraps the `List User Streams <https://developers.symphony.com/restapi/reference#list-user-streams>`_ endpoint.

        :param stream_filter: the stream searching criteria.
        :param skip: number of stream results to skip.
        :param limit: maximum number of streams to return.
        :return: the list of stream retrieved matching the search filter.
        """
        return await self._streams_api.v1_streams_list_post(filter=stream_filter, skip=skip, limit=limit,
                                                            session_token=await self._auth_session.session_token)

    async def list_all_streams(self, stream_filter: StreamFilter, chunk_size: int = 50, max_number: int = None) \
            -> AsyncGenerator[StreamAttributes, None]:
        """Returns an asynchronous of all the streams of which the requesting user is a member,
        sorted by creation date (ascending - oldest to newest).
        Wraps the `List User Streams <https://developers.symphony.com/restapi/reference#list-user-streams>`_ endpoint.

        :param stream_filter:  the stream searching criteria.
        :param chunk_size: the maximum number of elements to retrieve in one underlying HTTP call
        :param max_number: the total maximum number of elements to retrieve
        :return: an asynchronous generator of the streams matching the search filter.
        """

        async def list_streams_one_page(skip, limit):
            result = await self.list_streams(stream_filter, skip, limit)
            return result.value if result else None

        return offset_based_pagination(list_streams_one_page, chunk_size, max_number)

    async def add_member_to_room(self, user_id: int, room_id: str):
        """Adds a member to an existing room.
        Wraps the `Add Member <https://developers.symphony.com/restapi/reference#add-member>`_ endpoint.

        :param user_id: the id of the user to be added to the room.
        :param room_id: the id of the room in which to add the user.
        :return: None
        """
        await self._room_membership_api.v1_room_id_membership_add_post(
            payload=UserId(id=user_id), id=room_id,
            session_token=await self._auth_session.session_token)

    async def remove_member_from_room(self, user_id: int, room_id: str):
        """Removes a member from an existing room.
        Wraps the `Remove Member <https://developers.symphony.com/restapi/reference#remove-member>`_ endpoint.

        :param user_id: the id of the user to be removed from the room.
        :param room_id: the id of the room from which to remove the user.
        :return: None
        """
        await self._room_membership_api.v1_room_id_membership_remove_post(
            payload=UserId(id=user_id), id=room_id,
            session_token=await self._auth_session.session_token)

    async def share(self, stream_id: str, content: ShareContent) -> V2Message:
        """Share third-party content, such as a news article, into the specified stream.
        The stream can be a chat room, an IM, or an MIM.
        Wraps the `Share <https://developers.symphony.com/restapi/reference#share-v3>`_ endpoint.

        :param stream_id: the id of the stream in which to share the given content.
        :param content: the third-party content to be shared.
        :return: the created message.
        """
        return await self._share_api.v3_stream_sid_share_post(
            sid=stream_id, share_content=content, session_token=await self._auth_session.session_token,
            key_manager_token=await self._auth_session.key_manager_token)

    async def promote_user_to_room_owner(self, user_id: int, room_id: str):
        """Promotes user to owner of the chat room.
        Wraps the `Promote Owner <https://developers.symphony.com/restapi/reference#promote-owner>`_ endpoint.

        :param user_id: the id of the user to be promoted as owner.
        :param room_id: the room id.
        :return: None
        """
        await self._room_membership_api.v1_room_id_membership_promote_owner_post(
            id=room_id, payload=UserId(id=user_id), session_token=await self._auth_session.session_token)

    async def demote_owner_to_room_participant(self, user_id: int, room_id: str):
        """Demotes room owner to a participant in the chat room.
        Wraps the `Demote Owner <https://developers.symphony.com/restapi/reference#demote-owner>`_ endpoint.

        :param user_id: the id of the room owner to be demoted.
        :param room_id: the room id.
        :return: None
        """
        await self._room_membership_api.v1_room_id_membership_demote_owner_post(
            id=room_id, payload=UserId(id=user_id), session_token=await self._auth_session.session_token)


class StreamService(OboStreamService):
    """Service class to manage streams.
    """

    async def create_im_or_mim(self, user_ids: [int]) -> Stream:
        """Create a new single or multi party instant message conversation between the caller and specified users.
        The caller is implicitly included in the members of the created chat.
        Duplicate users will be included in the membership of the chat but the duplication will be silently ignored.
        If there is an existing IM conversation with the same set of participants then the id of that existing stream
        will be returned.
        If the given list of user ids contains only one id, an IM will be created, otherwise, a MIM will be created.

        Wraps the `Create IM or MIM <https://developers.symphony.com/restapi/reference#create-im-or-mim>`_ endpoint.

        :param user_ids: the list of user ids ti be put as room participants.
        :return: the created stream.
        """
        return await self._streams_api.v1_im_create_post(uid_list=UserIdList(value=user_ids),
                                                         session_token=await self._auth_session.session_token)

    async def create_room(self, room_attributes: V3RoomAttributes) -> V3RoomDetail:
        """Creates a new chatroom.
        If no  attributes are specified, the room is created as a private chatroom.
        Wraps the `Create Room V3 <https://developers.symphony.com/restapi/reference#create-room-v3>`_ endpoint.

        :param room_attributes: attributes of the room to be created.
        :return: details of created room.
        """
        return await self._streams_api.v3_room_create_post(payload=room_attributes,
                                                           session_token=await self._auth_session.session_token)

    async def search_rooms(self, query: V2RoomSearchCriteria, skip: int = 0,
                           limit: int = 50) -> V3RoomSearchResults:
        """Search for rooms according to the specified criteria.
        Wraps the `Search Rooms V3 <https://developers.symphony.com/restapi/reference#search-rooms-v3>`_ endpoint.

        :param query: the search criteria.
        :param skip: number of rooms to skip, defaults to 0.
        :param limit: number of maximum rooms to return. Must be a positive integer that does not exceed 100.
        :return: the rooms matching search criteria.
        """
        return await self._streams_api.v3_room_search_post(query=query, skip=skip, limit=limit,
                                                           session_token=await self._auth_session.session_token)

    async def search_all_rooms(self, query: V2RoomSearchCriteria, chunk_size: int = 50,
                               max_number: int = None) -> AsyncGenerator[V3RoomDetail, None]:
        """Search for rooms according to the specified criteria.
        Wraps the `Search Rooms V3 <https://developers.symphony.com/restapi/reference#search-rooms-v3>`_ endpoint.

        :param query: the search criteria.
        :param chunk_size: the maximum number of elements to retrieve in one underlying HTTP call.
        :param max_number: the total maximum number of elements to retrieve.
        :return: an asynchronous generator of the rooms matching the search criteria.
        """

        async def search_rooms_one_page(skip, limit):
            result = await self.search_rooms(query, skip, limit)
            return result.rooms if result.rooms else None

        return offset_based_pagination(search_rooms_one_page, chunk_size, max_number)

    async def get_room_info(self, room_id: str) -> V3RoomDetail:
        """Get information about a particular room.
        Wraps the `Room Info V3 <https://developers.symphony.com/restapi/reference#room-info-v3>`_ endpoint.

        :param room_id: the id of the room.
        :return: the room details.
        """
        return await self._streams_api.v3_room_id_info_get(id=room_id,
                                                           session_token=await self._auth_session.session_token)

    async def set_room_active(self, room_id: str, active: bool) -> RoomDetail:
        """Deactivates or reactivates a chatroom. At creation time, the chatroom is activated by default.
        Wraps the `De/Reactivate Room <https://developers.symphony.com/restapi/reference#de-or-re-activate-room>`_
        endpoint.

        :param room_id: the id of the room to be deactivated or reactivated.
        :param active: the new active status (True to reactivate, false to deactivate).
        :return: the details of the updated room.
        """
        return await self._streams_api.v1_room_id_set_active_post(id=room_id, active=active,
                                                                  session_token=await self._auth_session.session_token)

    async def update_room(self, room_id: str, room_attributes: V3RoomAttributes) -> V3RoomDetail:
        """Updates the attributes of an existing chatroom.
        Wraps the `Update Room V3 <https://developers.symphony.com/restapi/reference#update-room-v3>`_ endpoint.

        :param room_id: the id of the room to be updated.
        :param room_attributes: the attributes of the room to be updated.
        :return: the details of the updated room.
        """
        return await self._streams_api.v3_room_id_update_post(id=room_id, payload=room_attributes,
                                                              session_token=await self._auth_session.session_token)

    async def create_im_admin(self, user_ids: [int]) -> Stream:
        """Create a new single or multi party instant message conversation.
        At least two user IDs must be provided or an error response will be sent.
        The caller is not included in the members of the created chat.
        Duplicate users will be included in the membership of the chat but the duplication will be silently ignored.
        If there is an existing IM conversation with the same set of participants then the id of that existing stream
        will be returned.

        Wraps the
        `Create IM or MIM Non-inclusive <https://developers.symphony.com/restapi/reference#create-im-or-mim-admin>`_
        endpoint.

        :param user_ids: the list of user IDs to be put as participants. At least two user IDs must be provided.
        :return: the created IM or MIM.
        """
        return await self._streams_api.v1_admin_im_create_post(uid_list=UserIdList(value=user_ids),
                                                               session_token=await self._auth_session.session_token)

    async def set_room_active_admin(self, room_id: str, active: bool) -> RoomDetail:
        """Deactivates or reactivates a chatroom via AC Portal.

        :param room_id: the id of the room to be deactivated or reactivated.
        :param active: the new active status (True to reactivate, false to deactivate).
        :return: the details of the updated room.
        """
        return await self._streams_api.v1_admin_room_id_set_active_post(
            id=room_id, active=active,
            session_token=await self._auth_session.session_token)

    async def list_streams_admin(self, stream_filter: V2AdminStreamFilter, skip: int = 0,
                                 limit: int = 50) -> V2AdminStreamList:
        """Retrieves all the streams across the enterprise.
        Wraps the `List Streams for Enterprise V2
        <https://developers.symphony.com/restapi/reference#list-streams-for-enterprise-v2>`_ endpoint.

        :param stream_filter: the stream searching filter.
        :param skip: the number of streams to skip.
        :param limit: the maximum number of streams to retrieve. Must be a positive integer less or equal than 100.
        :return: the list of streams matching the search criteria.
        """
        return await self._streams_api.v2_admin_streams_list_post(filter=stream_filter, skip=skip, limit=limit,
                                                                  session_token=await self._auth_session.session_token)

    async def list_all_streams_admin(self, stream_filter: V2AdminStreamFilter, chunk_size=50, max_number=None) \
            -> AsyncGenerator[V2AdminStreamInfo, None]:
        """Retrieves all the streams across the enterprise.
        Wraps the `List Streams for Enterprise V2
        <https://developers.symphony.com/restapi/reference#list-streams-for-enterprise-v2>`_ endpoint.

        :param stream_filter: the stream searching filter.
        :param chunk_size: the maximum number of elements to retrieve in one underlying HTTP call.
        :param max_number: the total maximum number of elements to retrieve.
        :return: an asynchronous generator of streams matching the search criteria.
        """

        async def list_streams_admin_one_page(skip, limit):
            result = await self.list_streams_admin(stream_filter, skip, limit)
            return result.streams.value if result.streams else None

        return offset_based_pagination(list_streams_admin_one_page, chunk_size, max_number)

    async def list_stream_members(self, stream_id: str, skip: int = 0, limit: int = 100) -> V2MembershipList:
        """List the current members of an existing stream. The stream can be of type IM, MIM, or ROOM.
        Wraps the `Stream Members <https://developers.symphony.com/restapi/reference#stream-members>`_ endpoint.

        :param stream_id: the ID of the stream.
        :param skip: the number of members to skip.
        :param limit: the maximum number of members to retrieve. Must be less or equal than 1000.
        :return: the list of stream members.
        """
        return await self._streams_api.v1_admin_stream_id_membership_list_get(
            id=stream_id, skip=skip, limit=limit,
            session_token=await self._auth_session.session_token)

    async def list_all_stream_members(self, stream_id: str, chunk_size: int = 50, max_number=None) \
            -> AsyncGenerator[V2MemberInfo, None]:
        """List the current members of an existing stream. The stream can be of type IM, MIM, or ROOM.
        Wraps the `Stream Members <https://developers.symphony.com/restapi/reference#stream-members>`_ endpoint.

        :param stream_id: the ID of the stream.
        :param chunk_size: the maximum number of elements to retrieve in one underlying HTTP call.
        :param max_number: the total maximum number of elements to retrieve.
        :return: an asynchronous generator of the stream members.
        """
        async def list_stream_members_one_page(skip, limit):
            members = await self.list_stream_members(stream_id, skip, limit)
            return members.members.value if members.members else None

        return offset_based_pagination(list_stream_members_one_page, chunk_size, max_number)

    async def list_room_members(self, room_id: str) -> MembershipList:
        """Lists the current members of an existing room.
        Wraps the `Room Members <https://developers.symphony.com/restapi/reference#room-members>`_ endpoint.

        :param room_id: the ID of the room.
        :return: the list of room members.
        """
        return await self._room_membership_api.v2_room_id_membership_list_get(
            id=room_id,
            session_token=await self._auth_session.session_token)
