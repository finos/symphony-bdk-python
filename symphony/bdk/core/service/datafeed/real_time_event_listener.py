from symphony.bdk.gen import ApiAttributeError
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
    """Interface for a callback to be invoked when a RealTimeEvent is received from the datafeed
    `real-time-events <https://developers.symphony.com/restapi/docs/real-time-events>_`
    """

    @staticmethod
    async def is_accepting_event(event: V4Event, username: str) -> bool:
        """Checks if the event is accepted to be handled.

        By default, all the events that is created by the bot  itself will not be accepted to be handled by the
        listener. If you want to handle the self-created events or you want to apply your own filters for the events,
        you should override this method.

        :param event: Event to be verified.
        :param username: Username of the initiator.
        :return: True if the event is accepted, False otherwise
        """
        try:
            return event.initiator.user.username != username
        except ApiAttributeError:
            return False

    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        """ Called when a MESSAGESENT event is received.

        :param initiator: Event initiator.
        :param event: Message sent payload.
        """

    async def on_shared_post(self, initiator: V4Initiator, event: V4SharedPost):
        """ Called when an INSTANTMESSAGECREATED event is received.

        :param initiator: Event initiator.
        :param event:  Shared post payload.
        """

    async def on_instant_message_created(self, initiator: V4Initiator, event: V4InstantMessageCreated):
        """ Called when a ROOMCREATED event is received.

        :param initiator: Event initiator.
        :param event: Instant Message Created payload.
        """

    async def on_room_created(self, initiator: V4Initiator, event: V4RoomCreated):
        """

        :param initiator: Event initiator.
        :param event: Room Created payload.
        """

    async def on_room_updated(self, initiator: V4Initiator, event: V4RoomUpdated):
        """

        :param initiator: Event initiator.
        :param event: Room Updated payload.
        """

    async def on_room_deactivated(self, initiator: V4Initiator, event: V4RoomDeactivated):
        """

        :param initiator: Event initiator.
        :param event: Room Deactivated payload.
        """

    async def on_room_reactivated(self, initiator: V4Initiator, event: V4RoomReactivated):
        """

        :param initiator: Event initiator.
        :param event: Room Reactivated payload.
        """

    async def on_user_requested_to_join_room(self, initiator: V4Initiator, event: V4UserRequestedToJoinRoom):
        """

        :param initiator: Event initiator.
        :param event: User Requested To Join Room payload.
        """

    async def on_user_joined_room(self, initiator: V4Initiator, event: V4UserJoinedRoom):
        """

        :param initiator: Event initiator.
        :param event: User Joined Room payload.
        """

    async def on_user_left_room(self, initiator: V4Initiator, event: V4UserLeftRoom):
        """

        :param initiator: Event initiator.
        :param event: User Left Room payload.
        """

    async def on_room_member_promoted_to_owner(self, initiator: V4Initiator, event: V4RoomMemberPromotedToOwner):
        """

        :param initiator: Event initiator.
        :param event: Room Member Promoted To Owner payload.
        """

    async def on_room_demoted_from_owner(self, initiator: V4Initiator, event: V4RoomMemberDemotedFromOwner):
        """

        :param initiator: Event initiator.
        :param event: Room Member Demoted From Owner payload.
        """

    async def on_connection_requested(self, initiator: V4Initiator, event: V4ConnectionRequested):
        """

        :param initiator: Event initiator.
        :param event: Connection Requested payload.
        """

    async def on_connection_accepted(self, initiator: V4Initiator, event: V4ConnectionAccepted):
        """

        :param initiator: Event initiator.
        :param event: Connection Accepted payload.
        """

    async def on_message_suppressed(self, initiator: V4Initiator, event: V4MessageSuppressed):
        """

        :param initiator: Event initiator.
        :param event: Message Suppressed payload.
        """

    async def on_symphony_elements_action(self, initiator: V4Initiator, event: V4SymphonyElementsAction):
        """

        :param initiator: Event initiator.
        :param event: Symphony Elements Action payload.
        """
