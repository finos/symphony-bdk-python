from abc import ABC, abstractmethod

#Abstract class for ROOM listener
#class is just an interface of functions to handle the Room events recieved from DataFeed
#(see Real Time Events in REST API documentation for more details)
#the developer will handle actual event logic in your implementation of this abstract class
class RoomListener(ABC):

    @abstractmethod
    def onRoomMessage(self, message):
        pass

    @abstractmethod
    def onRoomCreated(self, roomCreated):
        pass

    @abstractmethod
    def onRoomDeactivated(self, roomDeactivated):
        pass

    @abstractmethod
    def onRoomMemberDemotedFromOwner(self, roomMemberDemotedFromOwner):
        pass

    @abstractmethod
    def onRoomMemberPromotedToOwner(self, roomMemberPromotedToOwner):
        pass

    @abstractmethod
    def onRoomReactivated(self, roomReactivated):
        pass

    @abstractmethod
    def onRoomUpdated(self, roomUpdated):
        pass

    @abstractmethod
    def onUserJoinedRoom(self, userJoinedRoom):
        pass

    @abstractmethod
    def onUserLeftRoom(self, userLeftRoom):
        pass
