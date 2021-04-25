from unittest.mock import MagicMock, AsyncMock, Mock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.stream.stream_service import StreamService
from symphony.bdk.gen import ApiClient, Configuration
from symphony.bdk.gen.agent_api.share_api import ShareApi
from symphony.bdk.gen.agent_model.share_content import ShareContent
from symphony.bdk.gen.agent_model.v2_message import V2Message
from symphony.bdk.gen.pod_api.room_membership_api import RoomMembershipApi
from symphony.bdk.gen.pod_api.streams_api import StreamsApi
from symphony.bdk.gen.pod_model.membership_list import MembershipList
from symphony.bdk.gen.pod_model.room_detail import RoomDetail
from symphony.bdk.gen.pod_model.stream import Stream
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
from tests.core.config import minimal_retry_config
from tests.utils.resource_utils import get_deserialized_object_from_resource

KM_TOKEN = "km_token"
SESSION_TOKEN = "session_token"


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = SESSION_TOKEN
    auth_session.key_manager_token = KM_TOKEN
    return auth_session


@pytest.fixture(name="mocked_api_client")
def fixture_mocked_api_client():
    api_client = MagicMock(ApiClient)
    api_client.call_api = AsyncMock()
    api_client.configuration = Configuration()
    return api_client


@pytest.fixture(name="streams_api")
def fixture_streams_api(mocked_api_client):
    return Mock(wraps=StreamsApi(mocked_api_client))


@pytest.fixture(name="room_membership_api")
def fixture_room_membership_api(mocked_api_client):
    return Mock(wraps=RoomMembershipApi(mocked_api_client))


@pytest.fixture(name="share_api")
def fixture_share_api(mocked_api_client):
    return Mock(wraps=ShareApi(mocked_api_client))


@pytest.fixture(name="stream_service")
def fixture_stream_service(streams_api, room_membership_api, share_api, auth_session):
    return StreamService(streams_api, room_membership_api, share_api, auth_session, minimal_retry_config())


@pytest.mark.asyncio
async def test_get_stream(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(V2StreamAttributes,
                                                                                    "stream/get_stream.json")

    stream_id = "stream_id"
    stream_attributes = await stream_service.get_stream(stream_id)

    streams_api.v2_streams_sid_info_get.assert_called_once_with(sid=stream_id, session_token=SESSION_TOKEN)
    assert stream_attributes.id == "ubaSiuUsc_j-_lVQ8vhAz3___opSJdJZdA"
    assert stream_attributes.room_attributes.name == "New room name"
    assert stream_attributes.stream_type.type == "ROOM"


@pytest.mark.asyncio
async def test_list_streams(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(StreamList,
                                                                                    "stream/list_streams.json")

    stream_filter = StreamFilter()
    skip = 1
    limit = 2

    streams = await stream_service.list_streams(stream_filter, skip, limit)

    streams_api.v1_streams_list_post.assert_called_once_with(filter=stream_filter, skip=skip, limit=limit,
                                                             session_token=SESSION_TOKEN)
    assert len(streams.value) == 2
    assert streams.value[0].id == "ouAS1QXEHtIhXdZq4NzJBX___oscpQFcdA"
    assert streams.value[0].room_attributes.name == "Room APP-3033"
    assert streams.value[1].id == "z22OMRPxSdRFBfH_oojGkn___orihaxrdA"
    assert streams.value[1].room_attributes.name == "Test BDK"


@pytest.mark.asyncio
async def test_list_all_streams(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(StreamList,
                                                                                    "stream/list_streams.json")

    stream_filter = StreamFilter()
    limit = 4

    gen = await stream_service.list_all_streams(stream_filter, limit)
    streams = [s async for s in gen]

    streams_api.v1_streams_list_post.assert_called_once_with(filter=stream_filter, skip=0, limit=limit,
                                                             session_token=SESSION_TOKEN)
    assert len(streams) == 2
    assert streams[0].id == "ouAS1QXEHtIhXdZq4NzJBX___oscpQFcdA"
    assert streams[0].room_attributes.name == "Room APP-3033"
    assert streams[1].id == "z22OMRPxSdRFBfH_oojGkn___orihaxrdA"
    assert streams[1].room_attributes.name == "Test BDK"


@pytest.mark.asyncio
async def test_add_member_to_room(stream_service, room_membership_api):

    user_id = 1234456
    room_id = "room_id"
    await stream_service.add_member_to_room(user_id, room_id)  # check no exception raised

    room_membership_api.v1_room_id_membership_add_post.assert_called_once_with(
        payload=UserId(id=user_id), id=room_id, session_token=SESSION_TOKEN)


@pytest.mark.asyncio
async def test_remove_member_from_room(stream_service, room_membership_api):

    user_id = 1234456
    room_id = "room_id"
    await stream_service.remove_member_from_room(user_id, room_id)  # check no exception raised

    room_membership_api.v1_room_id_membership_remove_post.assert_called_once_with(
        payload=UserId(id=user_id), id=room_id, session_token=SESSION_TOKEN)


@pytest.mark.asyncio
async def test_share(mocked_api_client, stream_service, share_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(V2Message,
                                                                                    "stream/share_article.json")

    stream_id = "stream_id"
    share_content = ShareContent()
    message = await stream_service.share(stream_id, share_content)

    share_api.v3_stream_sid_share_post.assert_called_once_with(
        sid=stream_id, share_content=share_content, session_token=SESSION_TOKEN, key_manager_token=KM_TOKEN)
    assert message.id == "uRcu9fjRALpKLHnPR1k6-3___oh4wwAObQ"
    assert message.stream_id == "ubaSiuUsc_j-_lVQ8vhAz3___opSJdJZdA"


@pytest.mark.asyncio
async def test_promote_user(stream_service, room_membership_api):

    user_id = 12345
    room_id = "room_id"
    await stream_service.promote_user_to_room_owner(user_id, room_id)  # check no exception raised

    room_membership_api.v1_room_id_membership_promote_owner_post.assert_called_once_with(
        id=room_id, payload=UserId(id=user_id), session_token=SESSION_TOKEN)


@pytest.mark.asyncio
async def test_demote_owner(stream_service, room_membership_api):

    user_id = 12345
    room_id = "room_id"
    await stream_service.demote_owner_to_room_participant(user_id, room_id)  # check no exception raised

    room_membership_api.v1_room_id_membership_demote_owner_post.assert_called_once_with(
        id=room_id, payload=UserId(id=user_id), session_token=SESSION_TOKEN)


@pytest.mark.asyncio
async def test_create_im(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(Stream,
                                                                                    "stream/create_im_or_mim.json")

    user_ids = [12334]
    stream = await stream_service.create_im_or_mim(user_ids)

    streams_api.v1_im_create_post.assert_called_once_with(uid_list=UserIdList(value=user_ids),
                                                          session_token=SESSION_TOKEN)
    assert stream.id == "-M8s5WG7K8lAP7cpIiuyTH___oh4zK8EdA"


@pytest.mark.asyncio
async def test_create_room(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(V3RoomDetail,
                                                                                    "stream/create_room.json")

    room_attributes = V3RoomAttributes()
    room_details = await stream_service.create_room(room_attributes)

    streams_api.v3_room_create_post.assert_called_once_with(payload=room_attributes, session_token=SESSION_TOKEN)
    assert room_details.room_attributes.name == "New fancy room"
    assert room_details.room_system_info.id == "7X1cP_3wMD4mr6rcp7j26X___oh4uDkVdA"


@pytest.mark.asyncio
async def test_search_rooms(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(V3RoomSearchResults,
                                                                                    "stream/search_rooms.json")

    search_criteria = V2RoomSearchCriteria(query="query")
    skip = 1
    limit = 2
    search_results = await stream_service.search_rooms(search_criteria, skip, limit)

    streams_api.v3_room_search_post.assert_called_once_with(query=search_criteria, skip=skip, limit=limit,
                                                            session_token=SESSION_TOKEN)
    assert search_results.count == 1
    assert len(search_results.rooms) == 1
    assert search_results.rooms[0].room_attributes.name == "New room name"


@pytest.mark.asyncio
async def test_search_all_rooms(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(V3RoomSearchResults,
                                                                                    "stream/search_rooms.json")

    search_criteria = V2RoomSearchCriteria(query="query")
    chunk_size = 3

    gen = await stream_service.search_all_rooms(search_criteria, chunk_size=chunk_size)
    search_results = [r async for r in gen]

    streams_api.v3_room_search_post.assert_called_once_with(query=search_criteria, skip=0, limit=chunk_size,
                                                            session_token=SESSION_TOKEN)
    assert len(search_results) == 1
    assert search_results[0].room_attributes.name == "New room name"


@pytest.mark.asyncio
async def test_get_room_info(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(V3RoomDetail,
                                                                                    "stream/get_room_info.json")

    room_id = "room_id"
    room_detail = await stream_service.get_room_info(room_id)

    streams_api.v3_room_id_info_get.assert_called_once_with(id=room_id, session_token=SESSION_TOKEN)
    assert room_detail.room_attributes.name == "New room name"
    assert room_detail.room_system_info.id == "ubaSiuUsc_j-_lVQ8vhAz3___opSJdJZdA"


@pytest.mark.asyncio
async def test_set_room_active(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(RoomDetail,
                                                                                    "stream/deactivate_room.json")

    room_id = "room_id"
    active = False
    room_detail = await stream_service.set_room_active(room_id, active)

    streams_api.v1_room_id_set_active_post.assert_called_once_with(id=room_id, active=active,
                                                                   session_token=SESSION_TOKEN)
    assert not room_detail.room_system_info.active


@pytest.mark.asyncio
async def test_update_room(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(V3RoomDetail,
                                                                                    "stream/update_room.json")

    room_id = "room_id"
    room_attributes = V3RoomAttributes()
    room_details = await stream_service.update_room(room_id, room_attributes)

    streams_api.v3_room_id_update_post.assert_called_once_with(id=room_id, payload=room_attributes,
                                                               session_token=SESSION_TOKEN)
    assert room_details.room_attributes.name == "Test bot room"
    assert room_details.room_system_info.id == "ubaSiuUsc_j-_lVQ8vhAz3___opSJdJZdA"


@pytest.mark.asyncio
async def test_create_im_admin(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(Stream,
                                                                                    "stream/create_im_or_mim.json")

    user_ids = [12334]
    stream = await stream_service.create_im_admin(user_ids)

    streams_api.v1_admin_im_create_post.assert_called_once_with(uid_list=UserIdList(value=user_ids),
                                                                session_token=SESSION_TOKEN)
    assert stream.id == "-M8s5WG7K8lAP7cpIiuyTH___oh4zK8EdA"


@pytest.mark.asyncio
async def test_set_room_active_admin(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(RoomDetail,
                                                                                    "stream/deactivate_room.json")

    room_id = "room_id"
    active = False
    room_detail = await stream_service.set_room_active_admin(room_id, active)

    streams_api.v1_admin_room_id_set_active_post.assert_called_once_with(id=room_id, active=active,
                                                                         session_token=SESSION_TOKEN)
    assert not room_detail.room_system_info.active


@pytest.mark.asyncio
async def test_list_streams_admin(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(V2AdminStreamList,
                                                                                    "stream/list_streams_admin.json")

    stream_filter = V2AdminStreamFilter()
    skip = 1
    limit = 2
    streams = await stream_service.list_streams_admin(stream_filter, skip, limit)

    streams_api.v2_admin_streams_list_post.assert_called_once_with(filter=stream_filter, skip=skip, limit=limit,
                                                                   session_token=SESSION_TOKEN)
    assert streams.limit == 2
    assert len(streams.streams.value) == 2
    assert streams.streams.value[0].id == "hpRd80zAUnLv3NMhLVF3Ln___o3ULKRDdA"
    assert streams.streams.value[1].id == "6hEzTqQjVPLLE9KgXLvsKn___o3TtL3ddA"


@pytest.mark.asyncio
async def test_list_all_streams_admin(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(V2AdminStreamList,
                                                                                    "stream/list_streams_admin.json")

    stream_filter = V2AdminStreamFilter()
    limit = 10

    gen = await stream_service.list_all_streams_admin(stream_filter, chunk_size=limit)
    streams = [s async for s in gen]

    streams_api.v2_admin_streams_list_post.assert_called_once_with(filter=stream_filter, skip=0, limit=limit,
                                                                   session_token=SESSION_TOKEN)
    assert len(streams) == 2
    assert streams[0].id == "hpRd80zAUnLv3NMhLVF3Ln___o3ULKRDdA"
    assert streams[1].id == "6hEzTqQjVPLLE9KgXLvsKn___o3TtL3ddA"


@pytest.mark.asyncio
async def test_list_stream_members(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(V2MembershipList,
                                                                                    "stream/list_stream_members.json")

    stream_id = "stream_id"
    skip = 1
    limit = 2
    members = await stream_service.list_stream_members(stream_id, skip, limit)

    streams_api.v1_admin_stream_id_membership_list_get.assert_called_once_with(id=stream_id, skip=skip, limit=limit,
                                                                               session_token=SESSION_TOKEN)
    assert members.count == 2
    assert len(members.members.value) == 2
    assert members.members.value[0].user.user_id == 13056700579872
    assert members.members.value[1].user.user_id == 13056700579891


@pytest.mark.asyncio
async def test_list_all_stream_members(mocked_api_client, stream_service, streams_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(V2MembershipList,
                                                                                    "stream/list_stream_members.json")

    stream_id = "stream_id"
    limit = 5
    gen = await stream_service.list_all_stream_members(stream_id, limit)
    members = [m async for m in gen]

    streams_api.v1_admin_stream_id_membership_list_get.assert_called_once_with(id=stream_id, skip=0, limit=limit,
                                                                               session_token=SESSION_TOKEN)
    assert len(members) == 2
    assert members[0].user.user_id == 13056700579872
    assert members[1].user.user_id == 13056700579891


@pytest.mark.asyncio
async def test_list_room_members(mocked_api_client, stream_service, room_membership_api):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(MembershipList,
                                                                                    "stream/list_room_members.json")

    room_id = "room_id"
    members = await stream_service.list_room_members(room_id)
    members = members.value

    room_membership_api.v2_room_id_membership_list_get.assert_called_once_with(id=room_id, session_token=SESSION_TOKEN)
    assert len(members) == 2
    assert members[0].id == 13056700579872
    assert members[1].id == 13056700579891
