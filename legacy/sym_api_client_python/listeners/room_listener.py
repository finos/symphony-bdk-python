from abc import ABC, abstractmethod

# Abstract class for ROOM listener
# class is just an interface of functions to handle the Room events received
# from DataFeed see Real Time Events in REST API documentation for more
# details. The developer will handle actual event logic in your implementation
# of this abstract class


class RoomListener(ABC):

    @abstractmethod
    def on_room_msg(self, message):
        pass

    @abstractmethod
    def on_room_created(self, roomCreated):
        pass

    @abstractmethod
    def on_room_deactivated(self, roomDeactivated):
        pass

    @abstractmethod
    def on_room_member_demoted_from_owner(self, roomMemberDemotedFromOwner):
        pass

    @abstractmethod
    def on_room_member_promoted_to_owner(self, roomMemberPromotedToOwner):
        pass

    @abstractmethod
    def on_room_reactivated(self, roomReactivated):
        pass

    @abstractmethod
    def on_room_updated(self, roomUpdated):
        pass

    @abstractmethod
    def on_user_joined_room(self, userJoinedRoom):
        pass

    @abstractmethod
    def on_user_left_room(self, userLeftRoom):
        pass
