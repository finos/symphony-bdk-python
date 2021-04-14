import logging

from symphony.bdk.core.activity.api import AbstractActivity, ActivityContext
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_user_joined_room import V4UserJoinedRoom

logger = logging.getLogger(__name__)


class UserJoinedRoomContext(ActivityContext[V4UserJoinedRoom]):
    """
    Default implementation of the :py:class`ActivityContext` handled by the :py:class:`UserJoinedRoomActivity`
    """

    def __init__(self, initiator: V4Initiator, source_event: V4UserJoinedRoom):
        self._stream_id = source_event.stream.stream_id
        self._affected_user_id = source_event.affected_user.user_id
        super().__init__(initiator, source_event)

    @property
    def stream_id(self) -> str:
        return self._stream_id

    @property
    def affected_user_id(self) -> int:
        return self._affected_user_id


class UserJoinedRoomActivity(AbstractActivity[UserJoinedRoomContext]):
    """
    A form reply activity corresponds to a User joining a room .
    """

    def matches(self, context: UserJoinedRoomContext) -> bool:
        pass

    def on_activity(self, context: UserJoinedRoomContext):
        pass
