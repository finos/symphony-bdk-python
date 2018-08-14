import json
import logging
from .listeners import ConnectionListener
from .listeners import imListener
from .listeners import RoomListener
from .exceptions.UnauthorizedException import UnauthorizedException

#class handles the the creation and reading of DataFeed
#also contains the functionality to  dispatch the events coming back from the dataFeed
#sends data over to listener where the event is handled
class DataFeedEventService():

    def __init__(self, symBotClient):
        self.botClient = symBotClient
        self.dataFeedId = None
        self.datafeedEvents = []
        self.roomListeners = []
        self.IMListeners = []
        self.connectionListener =[]
        self.stop = False
        self.dataFeedClient = self.botClient.getDataFeedClient()

    def startDataFeed(self):
        logging.info('DataFeedEventService/startDataFeed()')
        self.dataFeedId = self.dataFeedClient.createDatafeed()
        self.readDatafeed(self.dataFeedId)

    def addRoomListener(self, roomlistener):
        self.roomListeners.append(roomlistener);

    def removeRoomListener(self, roomlistener):
        self.roomListeners.remove(roomlistener);

    def addIMListener(self, IMListener):
        self.IMListeners.append(IMListener);

    def removeIMListener(self, IMListener):
        self.IMListeners.remove(IMListener);

    def addConnectionsListener(self, connectionListener):
        self.connectionListeners.append(connectionListener);

    def removeConnectionsListener(self, connectionListener):
        self.connectionListeners.remove(connectionListener);

    def activateDataFeed(self):
        if self.stop == True:
            self.stop == False

    def deactivateDataFeed(self):
        if self.stop == False:
            self.stop == True

    #readDatafeed function reads an array of events coming back from DataFeedClient
    #checks to see that sender's email is not equal to Bot's email in config file
    #this functionality helps bot avoid entering an infinite loop where it responsds to its own messageSent
    def readDatafeed(self, id):
        while not self.stop:
            try:
                data = self.dataFeedClient.readDatafeed(id)
                if data:
                    finalData = data[0]
                    logging.debug('DataFeedEventService/readDatafeed() --> Incoming data from readDatafeed(): {}'.format(finalData[0]['payload']))
                    for i in range(0, len(finalData)):
                        if finalData[i]['initiator']['user']['email'] != self.botClient.config.data['botEmailAddress']:
                            self.handle_event(finalData[i])
                    # self.readDatafeed(id)
                else:
                    logging.debug('DataFeedEventService() - no data coming in from datafeed --> readDatafeed()')
                    # self.readDatafeed(id)

            except UnauthorizedException:
                logging.debug('DataFeedEventService - caught unauthorized exception --> startDataFeed()')
                self.startDataFeed()

    #function takes in single event --> Checks eventType --> forwards event to proper handling function
    def handle_event(self, payload):
        print('event handler')
        eventType = str(payload['type'])
        if eventType == 'MESSAGESENT':
            self.messageSentHandler(payload)
        elif eventType == 'INSTANTMESSAGECREATED':
            self.instantMessageHandler(payload)
        elif eventType == 'ROOMCREATED':
            self.roomCreatedHandler(payload)
        elif eventType == 'ROOMDEACTIVATED':
            self.roomDeactivatedHandler(payload)
        elif eventType == 'ROOMREACTIVATED':
            self.roomReactivatedHandler(payload)
        elif eventType == 'USERJOINEDROOM':
            self.userJoinedRoomHandler(payload)
        elif eventType == 'USERLEFTROOM':
            self.userLeftRoomHandler(payload)
        elif eventType == 'ROOMMEMBERPROMOTEDTOOWNER':
            self.promotedToOwner(payload)
        elif eventType == 'ROOMMEMBERDEMOTEDFROMOWNER':
            self.demotedToOwner(payload)
        elif eventType == 'CONNECTIONACCEPTED':
            self.connectionAcceptedHandler(payload)
        elif eventType == 'CONNECTIONREQUESTED':
            self.connectionRequestedHandler(payload)
        else:
            logging.debug('no event detected')
            return

    #check streamType --> send data to appropriate listener
    def messageSentHandler(self, payload):
        logging.debug('messageSentHandler function started')
        streamType = payload['payload']['messageSent']['message']['stream']['streamType']
        messageSentData = payload['payload']
        if (str(streamType) == 'ROOM'):
            for listener in self.roomListeners:
                listener.onRoomMessage(messageSentData)
        else:
            for listener in self.IMListeners:
                listener.onIMMessage(messageSentData)


    def instantMessageHandler(self, payload):
        logging.debug('instantMessageHandler fucntion started')
        instantMessageData = payload['payload']
        logging.debug(instantMessageData)
        for listener in self.IMListeners:
            listener.onIMCreated(instantMessageData)

    def roomCreatedHandler(self, payload):
        logging.debug('roomCreatedHandler function started')
        roomCreatedData = payload['payload']
        logging.debug(roomCreatedData)
        for listener in self.roomListeners:
            listener.onRoomCreated(roomCreatedData)
            break

    def roomUpdatedHandler(self, payload):
        logging.debugrint('roomUpdatedHandler')
        roomUpdatedData = payload['payload']
        logging.debug(roomUpdatedData)
        for listener in self.roomListeners:
            listener.onRoomUpdated(roomUpdatedData)

    def roomDeactivatedHandler(self, payload):
        logging.debug('roomDeactivatedHandler')
        roomDeactivatedData = payload['payload']
        logging.debug(roomDeactivatedData)
        for listner in self.roomListeners:
            listener.onRoomDeactivated(roomDeactivatedData)

    def roomReactivatedHandler(self, payload):
        logging.debug('roomReactivatedHandler')
        roomReactivatedData = payload['payload']
        logging.debug(roomReactivatedData)
        for listener in self.roomListeners:
            listener.onRoomReactivated(roomReactivatedData)

    def userJoinedRoomHandler(self, payload):
        logging.debug('userJoinedRoomHandler')
        userJoinedRoomData = payload['payload']
        logging.debug(userJoinedRoomData)
        for listener in self.roomListeners:
            listener.onUserJoinedRoom(userJoinedRoomData)

    def userLeftRoomHandler(self, payload):
        logging.debug('userLeftRoomHandler')
        userLeftRoomData = payload['payload']
        logging.debug(userLeftRoomData)
        for listener in self.roomListeners:
            listener.onUserLeftRoom(userLeftRoomData)

    def promotedToOwner(self, payload):
        logging.debug('promotedToOwner')
        promotedToOwnerData = payload['payload']
        logging.debug(promotedToOwnerData)
        for listener in self.roomListeners:
            listener.onRoomMemberPromotedToOwner(promotedToOwnerData)

    def demotedToOwner(self, payload):
        logging.debug('demotedtoOwner')
        demotedToOwnerData = payload['payload']
        logging.debug(demotedToOwnerData)
        for listener in self.roomListeners:
            listener.onRoomMemberDemotedFromOwner(demotedToOwnerData)

    def connectionAcceptedHandler(self, payload):
        logging.debug('connectionAcceptedHandler')
        connectionAcceptedData = payload['payload']
        logging.debug(connectionAcceptedData)
        for listener in self.connectionListeners:
            listener.onConnectionAccepted(connectionAcceptedData)

    def connectionRequestedHandler(self, payload):
        logging.debug('connectionRequestedHandler')
        connectionRequestedData = payload['payload']
        logging.debug(connectionRequestedData)
        for listener in self.connectionListeners:
            listener.onConnectionRequested(connectionRequestedData)
