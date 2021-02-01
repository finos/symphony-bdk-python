from abc import ABC, abstractmethod

from symphony.bdk.gen.agent_model.v4_event import V4Event
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_shared_post import V4SharedPost
from symphony.bdk.gen.agent_model.v4_instant_message_created import V4InstantMessageCreated
from symphony.bdk.gen.agent_model.v4_room_created import V4RoomCreated
from symphony.bdk.gen.agent_model.v4_room_updated import V4RoomUpdated
from symphony.bdk.gen.agent_model.v4_room_deactivated import V4RoomDeactivated
from symphony.bdk.gen.agent_model.v4_room_reactivated import V4RoomReactivated
from symphony.bdk.gen.agent_model.v4_user_requested_to_join_room import V4UserRequestedToJoinRoom
from symphony.bdk.gen.agent_model.v4_user_joined_room import V4UserJoinedRoom
from symphony.bdk.gen.agent_model.v4_user_left_room import V4UserLeftRoom
from symphony.bdk.gen.agent_model.v4_room_member_promoted_to_owner import V4RoomMemberPromotedToOwner
from symphony.bdk.gen.agent_model.v4_room_member_demoted_from_owner import V4RoomMemberDemotedFromOwner
from symphony.bdk.gen.agent_model.v4_connection_requested import V4ConnectionRequested
from symphony.bdk.gen.agent_model.v4_connection_accepted import V4ConnectionAccepted
from symphony.bdk.gen.agent_model.v4_message_suppressed import V4MessageSuppressed
from symphony.bdk.gen.agent_model.v4_symphony_elements_action import V4SymphonyElementsAction


class RealTimeEventListener:
    """Interface for a callback to be invoked when a RealTimeEvent is received  from the datafeed
    `real-time-events <https://developers.symphony.com/restapi/docs/real-time-events>_`

    """

    def is_accepting_event(self, event: V4Event, username: str) -> bool:
        # should check if the event is passed correctly.
        # i.e is the event passed possibly None, empty ..etc
        initiator = event.initiator
        user = initiator.user
        initiator_username = user.username
        return initiator_username is not None and not (initiator_username == username)

    def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        pass

    def on_shared_post(self, initiator: V4Initiator, event: V4SharedPost):
        pass

    def on_instant_message_created(self, initiator: V4Initiator, event: V4InstantMessageCreated):
        pass

    def on_room_created(self, initiator: V4Initiator, event: V4RoomCreated):
        pass

    def on_room_updated(self, initiator: V4Initiator, event: V4RoomUpdated):
        pass

    def on_room_deactivated(self, initiator: V4Initiator, event: V4RoomDeactivated):
        pass

    def on_room_reactivated(self, initiator: V4Initiator, event: V4RoomReactivated):
        pass

    def on_user_requested_to_join_room(self, initiator: V4Initiator, event: V4UserRequestedToJoinRoom):
        pass

    def on_user_joined_room(self, initiator: V4Initiator, event: V4UserJoinedRoom):
        pass

    def on_user_left_room(self, initiator: V4Initiator, event: V4UserLeftRoom):
        pass

    def on_room_member_promoted_to_owner(self, initiator: V4Initiator, event: V4RoomMemberPromotedToOwner):
        pass

    def on_room_demoted_from_owner(self, initiator: V4Initiator, event: V4RoomMemberDemotedFromOwner):
        pass

    def on_connection_requested(self, initiator: V4Initiator, event: V4ConnectionRequested):
        pass

    def on_connection_accepted(self, initiator: V4Initiator, event: V4ConnectionAccepted):
        pass

    def on_message_suppressed(self, initiator: V4Initiator, event: V4MessageSuppressed):
        pass

    def on_symphony_elements_action(self, initiator: V4Initiator, event: V4SymphonyElementsAction):
        pass
