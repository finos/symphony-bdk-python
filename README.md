# symphony-api-client-python
The Python client is built in an event handler architecture. If you are building a bot that listens to conversations, you will only have to implement an interface of a listener with the functions to handle all events that will come through the Data Feed.

### Install: pip install sym-api-client-python
### Note this repo is in constant development


## Configuration
There are two methods of authentication.  You can either authenticate your bot using certificates or using RSA.  If you are going to authenticate using certificates, make sure you have a config.json file in your project which includes the following properties:

        {
          "sessionAuthHost": "COMPANYNAME-api.symphony.com",
          "sessionAuthPort": 8444,
          "keyAuthHost": "COMPANYNAME-api.symphony.com",
          "keyAuthPort": 8444,
          "podHost": "COMPANYNAME.symphony.com",
          "podPort": 443,
          "agentHost": "COMAPNYNAME.symphony.com",
          "agentPort": 443,
          "botCertPath": "PATH",
          "botCertName": "BOT-CERT-NAME",
          "botCertPassword": "BOT-PASSWORD",
          "botEmailAddress": "BOT-EMAIL-ADDRESS",
          "appCertPath": "",
          "appCertName": "",
          "appCertPassword": "",
          "proxyURL": "",
          "proxyPort": "",
          "proxyUsername": "",
          "proxyPassword": "",
          "authTokenRefreshPeriod": "30"
        }

If you are going to authenticate using RSA, use the following rsa_config.json file:

        {
          "sessionAuthHost": "COMPANYNAME-api.symphony.com",
          "sessionAuthPort": 8444,
          "keyAuthHost": "COMPANYNAME-api.symphony.com",
          "keyAuthPort": 8444,
          "podHost": "COMPANYNAME.symphony.com",
          "podPort": 443,
          "agentHost": "COMAPNYNAME.symphony.com",
          "agentPort": 443,
          "botRSAPath": "PATH-TO-PRIVATEKEY",
          "botRSAName": "PRIVATEKEY.PEM-NAME",
          "botUsername": "BOT-USERNAME",
          "botEmailAddress": "BOT-EMAIL-ADDRESS",
          "appCertPath": "",
          "appCertName": "",
          "appCertPassword": "",
          "proxyURL": "",
          "proxyPort": "",
          "proxyUsername": "",
          "proxyPassword": "",
          "authTokenRefreshPeriod": "30"
        }

## Example main class (using certificates)

    from sym_api_client_python.configure.configure import SymConfig
    from sym_api_client_python.auth.auth import Auth
    from sym_api_client_python.clients.SymBotClient import SymBotClient
    from sym_api_client_python.listeners.imListenerTestImp import IMListenerTestImp
    from sym_api_client_python.listeners.roomListenerTestImp import RoomListenerTestImp
    #debug logging --> set to debug --> check logs/example.log
    import logging
    logging.basicConfig(filename='sym_api_client_python/logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    #main() acts as executable script --> run python3 hello.py to start Bot...

    #adjust global variable below to auth either using RSA or certificates

    def main():
            print('hi')
            #RSA Auth flow:
            #certificate Auth flow:
            configure = SymConfig('sym_api_client_python/resources/config.json')
            configure.loadFromFile()
            auth = Auth(configure)
            auth.authenticate()
            #initialize SymBotClient with auth and configure objects
            botClient = SymBotClient(auth, configure)
            #initialize datafeed service
            DataFeedEventService = botClient.getDataFeedEventService()
            #initialize listener classes and append them to DataFeedEventService class
            #these listener classes sit in DataFeedEventService class as a way to easily handle events
            #coming back from the DataFeed
            imListenerTest = IMListenerTestImp(botClient)
            DataFeedEventService.addIMListener(imListenerTest)
            roomListenerTest = RoomListenerTestImp(botClient)
            DataFeedEventService.addRoomListener(roomListenerTest)
            #create data feed and read datafeed recursively
            print('starting datafeed')
            DataFeedEventService.startDataFeed()

    if __name__ == "__main__":
        main()

## Example main class (using RSA)

    from sym_api_client_python.configure.configure import SymConfig
    from sym_api_client_python.auth.auth import Auth
    from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
    from sym_api_client_python.clients.SymBotClient import SymBotClient
    from sym_api_client_python.listeners.imListenerTestImp import IMListenerTestImp
    from sym_api_client_python.listeners.roomListenerTestImp import RoomListenerTestImp
    #debug logging --> set to debug --> check logs/example.log
    import logging
    logging.basicConfig(filename='sym_api_client_python/logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    #main() acts as executable script --> run python3 hello.py to start Bot...

    #adjust global variable below to auth either using RSA or certificates

    def main():
            print('hi')
            #RSA Auth flow:
            configure = SymConfig('sym_api_client_python/resources/rsa_config.json')
            configure.loadFromRSA()
            auth = SymBotRSAAuth(configure)
            auth.authenticate()
            #initialize SymBotClient with auth and configure objects
            botClient = SymBotClient(auth, configure)
            #initialize datafeed service
            DataFeedEventService = botClient.getDataFeedEventService()
            #initialize listener classes and append them to DataFeedEventService class
            #these listener classes sit in DataFeedEventService class as a way to easily handle events
            #coming back from the DataFeed
            imListenerTest = IMListenerTestImp(botClient)
            DataFeedEventService.addIMListener(imListenerTest)
            roomListenerTest = RoomListenerTestImp(botClient)
            DataFeedEventService.addRoomListener(roomListenerTest)
            #create data feed and read datafeed recursively
            print('starting datafeed')
            DataFeedEventService.startDataFeed()

    if __name__ == "__main__":
        main()


## Example RoomListener implementation

    from .RoomListener import RoomListener
    import calendar
    import time
    import logging
    #sample implementation of Abstract RoomListener class
    #has instance of SymBotClient so that it can respond to events coming in by leveraging other clients on SymBotClient
    #each function should contain logic for each corresponding event
    class RoomListenerTestImp(RoomListener):

        def __init__(self, SymBotClient):
            self.botClient = SymBotClient

        def onRoomMessage(self, message):
            logging.debug('room message recieved', message)
            #sample code for developer to implement --> use MessageClient and
            #data recieved from message event to reply with a #ReedF
            streamId = message['stream']['streamId']
            message = dict(message = '<messageML><hash tag="ReedF"/></messageML>')
            self.botClient.getMessageClient().sendMessage(streamId, message)

        def onRoomCreated(self, roomCreated):
            logging.debug('room created', roomCreated)

        def onRoomDeactivated(self, roomDeactivated):
            logging.debug('room Deactivated', roomDeactivated)

        def onRoomMemberDemotedFromOwner(self, roomMemberDemotedFromOwner):
            logging.debug('room member demoted from owner', roomMemberDemotedFromOwner)

        def onRoomMemberPromotedToOwner(self, roomMemberPromotedToOwner):
            logging.debug('room member promoted to owner', roomMemberPromotedToOwner)

        def onRoomReactivated(self, roomReactivated):
            logging.debug('room reactivated', roomReactivated)

        def onRoomUpdated(self, roomUpdated):
            logging.debug('room updated', roomUpdated)

        def onUserJoinedRoom(self, userJoinedRoom):
            logging.debug('USER JOINED ROOM', userJoinedRoom)

        def onUserLeftRoom(self, userLeftRoom):
            logging.debug('USER LEFT ROOM', userLeftRoom)
