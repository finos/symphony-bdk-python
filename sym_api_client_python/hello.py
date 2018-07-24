from configure.configure import Config
from auth.auth import Auth
from clients.SymBotClient import SymBotClient
from listeners.imListenerTestImp import IMListenerTestImp
from listeners.roomListenerTestImp import RoomListenerTestImp
#main() acts as executable script --> run python3 hello.py to start Bot...
def main():
        print('hi')
        #pass in path to config.json file to Config class
        configure = Config('./resources/config.json')
        #parse through config.json and extract decrypt certificates
        configure.connect()
        #if you wish to authenticate using RSA replace following line with: auth = rsa_Auth(configure) --> get rid of auth.authenticate
        auth = Auth(configure)
        #retrieve session and keymanager tokens:
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
        DataFeedEventService.startDataFeed()

if __name__ == "__main__":
    main()
