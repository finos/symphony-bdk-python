from unittest.mock import MagicMock, AsyncMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.stream.stream_service import StreamService
from symphony.bdk.gen import ApiClient, Configuration
from symphony.bdk.gen.agent_api.share_api import ShareApi
from symphony.bdk.gen.agent_model.share_content import ShareContent
from symphony.bdk.gen.pod_api.room_membership_api import RoomMembershipApi
from symphony.bdk.gen.pod_api.streams_api import StreamsApi
from symphony.bdk.gen.pod_model.stream_filter import StreamFilter
from symphony.bdk.gen.pod_model.stream_type import StreamType
from symphony.bdk.gen.pod_model.v2_admin_stream_filter import V2AdminStreamFilter
from symphony.bdk.gen.pod_model.v2_room_search_criteria import V2RoomSearchCriteria
from symphony.bdk.gen.pod_model.v2_stream_attributes import V2StreamAttributes
from symphony.bdk.gen.pod_model.v3_room_attributes import V3RoomAttributes
from tests.utils.resource_utils import object_from_json_relative_path


@pytest.fixture()
def auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = 'session_token'
    auth_session.key_manager_token = 'km_token'
    return auth_session


@pytest.fixture()
def mocked_api_client():
    api_client = MagicMock(ApiClient)
    api_client.call_api = AsyncMock()
    api_client.configuration = Configuration()
    return api_client


@pytest.fixture()
def stream_service(mocked_api_client, auth_session):
    return StreamService(StreamsApi(mocked_api_client), RoomMembershipApi(mocked_api_client),
                         ShareApi(mocked_api_client), auth_session)


@pytest.mark.asyncio
async def test_get_stream(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/get_stream.json")
    stream_attributes = await stream_service.get_stream("stream_id")

    assert stream_attributes.id == "ubaSiuUsc_j-_lVQ8vhAz3___opSJdJZdA"
    assert stream_attributes.streamType.type == "ROOM"
    assert stream_attributes.roomAttributes.name == "New room name"


@pytest.mark.asyncio
async def test_list_streams(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/list_streams.json")
    streams = await stream_service.list_streams(StreamFilter())

    assert len(streams) == 2

    assert streams[0].id == "ouAS1QXEHtIhXdZq4NzJBX___oscpQFcdA"
    assert streams[0].roomAttributes.name == "Room APP-3033"

    assert streams[1].id == "z22OMRPxSdRFBfH_oojGkn___orihaxrdA"
    assert streams[1].roomAttributes.name == "Test BDK"


@pytest.mark.asyncio
async def test_add_member_to_room(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/add_member.json")
    await stream_service.add_member_to_room(1234456, "room_id")  # check no exception raised


@pytest.mark.asyncio
async def test_remove_member_from_room(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/remove_member.json")
    await stream_service.remove_member_from_room(1234456, "room_id")  # check no exception raised


@pytest.mark.asyncio
async def test_share(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/share_article.json")
    message = await stream_service.share("stream_id", ShareContent())

    assert message.id == "uRcu9fjRALpKLHnPR1k6-3___oh4wwAObQ"
    assert message.streamId == "ubaSiuUsc_j-_lVQ8vhAz3___opSJdJZdA"


@pytest.mark.asyncio
async def test_promote_user(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/member_promoted.json")
    await stream_service.promote_user_to_room_owner(12345, "room_id")  # check no exception raised


@pytest.mark.asyncio
async def test_demote_owner(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/member_demoted.json")
    await stream_service.demote_owner_to_room_participant(12345, "room_id")  # check no exception raised


@pytest.mark.asyncio
async def test_get_stream(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/get_stream.json")
    stream_attributes = await stream_service.get_stream("stream_id")

    assert stream_attributes.id == "ubaSiuUsc_j-_lVQ8vhAz3___opSJdJZdA"
    assert stream_attributes.roomAttributes.name == "New room name"
    assert stream_attributes.streamType.type == "ROOM"


@pytest.mark.asyncio
async def test_create_im(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/create_im_or_mim.json")
    stream = await stream_service.create_im_or_mim([12334])

    assert stream.id == "-M8s5WG7K8lAP7cpIiuyTH___oh4zK8EdA"


@pytest.mark.asyncio
async def test_create_room(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/create_room.json")
    room_details = await stream_service.create_room(V3RoomAttributes())

    assert room_details.roomAttributes.name == "New fancy room"
    assert room_details.roomSystemInfo.id == "7X1cP_3wMD4mr6rcp7j26X___oh4uDkVdA"


@pytest.mark.asyncio
async def test_search_rooms(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/search_rooms.json")
    search_results = await stream_service.search_rooms(V2RoomSearchCriteria(query="query"))

    assert search_results.count == 1
    assert len(search_results.rooms) == 1
    assert search_results.rooms[0].roomAttributes.name == "New room name"


@pytest.mark.asyncio
async def test_get_room_info(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/get_room_info.json")
    room_detail = await stream_service.get_room_info("room_id")

    assert room_detail.roomAttributes.name == "New room name"
    assert room_detail.roomSystemInfo.id == "ubaSiuUsc_j-_lVQ8vhAz3___opSJdJZdA"


@pytest.mark.asyncio
async def test_set_room_active(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/deactivate_room.json")
    room_detail = await stream_service.set_room_active("room_id", False)

    assert not room_detail.roomSystemInfo.active


@pytest.mark.asyncio
async def test_update_room(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/update_room.json")
    room_details = await stream_service.update_room("room_id", V3RoomAttributes())

    assert room_details.roomAttributes.name == "Test bot room"
    assert room_details.roomSystemInfo.id == "ubaSiuUsc_j-_lVQ8vhAz3___opSJdJZdA"


@pytest.mark.asyncio
async def test_create_im_admin(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/create_im_or_mim.json")
    stream = await stream_service.create_im_admin([12334])

    assert stream.id == "-M8s5WG7K8lAP7cpIiuyTH___oh4zK8EdA"


@pytest.mark.asyncio
async def test_set_room_active_admin(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/deactivate_room.json")
    room_detail = await stream_service.set_room_active_admin("room_id", False)

    assert not room_detail.roomSystemInfo.active


@pytest.mark.asyncio
async def test_list_streams_admin(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/list_streams_admin.json")
    streams = await stream_service.list_streams_admin(V2AdminStreamFilter())

    assert streams.limit == 2
    assert len(streams.streams) == 2
    assert streams.streams[0].id == "hpRd80zAUnLv3NMhLVF3Ln___o3ULKRDdA"
    assert streams.streams[1].id == "6hEzTqQjVPLLE9KgXLvsKn___o3TtL3ddA"


@pytest.mark.asyncio
async def test_list_stream_members(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/list_stream_members.json")
    members = await stream_service.list_stream_members("stream_id")

    assert members.count == 2
    assert len(members.members) == 2
    assert members.members[0].user.userId == 13056700579872
    assert members.members[1].user.userId == 13056700579891


@pytest.mark.asyncio
async def test_list_room_members(mocked_api_client, stream_service):
    mocked_api_client.call_api.return_value = object_from_json_relative_path("stream/list_room_members.json")
    members = await stream_service.list_room_members("room_id")

    assert len(members) == 2
    assert members[0].id == 13056700579872
    assert members[1].id == 13056700579891
