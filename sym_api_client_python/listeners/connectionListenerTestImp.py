from listeners.ConnectionListener import ConnectionListener

#sample implementation of Abstract imListener class
#has instance of SymBotClient so that it can respond to events coming in by leveraging other clients on SymBotClient
#each function should contain logic for each corresponding event
class ConnectionListenerTestImp(IMListener):

    def __init__(self, SymBotClient):
        self.botClient = SymBotClient

    def onConnectionAccepted(self, connection):
        debug.log('onConnectionAccepted()', connection)

    def onConnectionRequested(self, connection):
        debug.log('onConnectionRequested', connection)
