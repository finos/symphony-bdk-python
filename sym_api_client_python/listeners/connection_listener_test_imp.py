from .connection_listener import ConnectionListener
import logging

# sample implementation of Abstract imListener class
# has instance of SymBotClient so that it can respond to events coming in by
# leveraging other clients on SymBotClient
# each function should contain logic for each corresponding event


class ConnectionListenerTestImp(ConnectionListener):
    """Example implementation of ConnectionListener

        sym_bot_client: contains clients which respond to incoming events

    """

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client

    def on_connection_accepted(self, connection):
        logging.debug('on_connection_accepted()', connection)

    def on_connection_requested(self, connection):
        logging.debug('on_connection_requested', connection)
