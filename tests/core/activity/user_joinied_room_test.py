import pytest
from symphony.bdk.gen.agent_model.v4_user import V4User

from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_stream import V4Stream
from symphony.bdk.gen.agent_model.v4_user_joined_room import V4UserJoinedRoom

from symphony.bdk.core.activity.user_joined_room import UserJoinedRoomActivity, UserJoinedRoomContext


@pytest.fixture(name="activity")
def fixture_activty():
    class TestUserJoinedRoomActivity(UserJoinedRoomActivity):
        """Dummy test User Joined Room Activty"""
        pass

    return TestUserJoinedRoomActivity()


@pytest.fixture(name="context")
def fixture_context():
    return UserJoinedRoomContext(V4Initiator(),
                                 V4UserJoinedRoom(stream=V4Stream(stream_id="12345678"),
                                                  affected_user=V4User(user_id=0)))


def test_matcher(activity, context):
    def dummy_matcher(passed_context: UserJoinedRoomContext):
        return passed_context.stream_id == "12345678"

    activity.matches = dummy_matcher

    context._stream_id = "12345678"
    assert activity.matches(context)

    context._stream_id = "000111122223233"
    assert not activity.matches(context)


def test_before_matcher(activity, context):
    activity.before_matcher(context)

    assert context.stream_id == "12345678"
