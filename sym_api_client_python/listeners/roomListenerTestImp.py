from listeners.RoomListener import RoomListener
import calendar;
import time;

#sample implementation of Abstract RoomListener class
#has instance of SymBotClient so that it can respond to events coming in by leveraging other clients on SymBotClient
#each function should contain logic for each corresponding event
class RoomListenerTestImp(RoomListener):

    def __init__(self, SymBotClient):
        self.botClient = SymBotClient

    def onRoomMessage(self, message):
        print('room message recieved', message)
        #sample code for developer to implement --> use MessageClient and
        #data recieved from message event to reply with a #reed
        streamId = message['payload']['messageSent']['message']['stream']['streamId']
        messageId = message['payload']['messageSent']['message']['messageId']
        message = dict(message = '<messageML><hash tag="reed"/></messageML>')
        self.botClient.messageClient.createMessage(streamId, message)

    def onRoomCreated(self, roomCreated):
        print('room created', roomCreated)

    def onRoomDeactivated(self, roomDeactivated):
        print('room Deactivated', roomDeactivated)

    def onRoomMemberDemotedFromOwner(self, roomMemberDemotedFromOwner):
        print('room member demoted from owner', roomMemberDemotedFromOwner)

    def onRoomMemberPromotedToOwner(self, roomMemberPromotedToOwner):
        print('room member promoted to owner', roomMemberPromotedToOwner)

    def onRoomReactivated(self, roomReactivated):
        print('room reactivated', roomReactivated)

    def onRoomUpdated(self, roomUpdated):
        print('room updated', roomUpdated)

    def onUserJoinedRoom(self, userJoinedRoom):
        print('USER JOINED ROOM', userJoinedRoom)

    def onUserLeftRoom(self, userLeftRoom):
        print('USER LEFT ROOM', userLeftRoom)
