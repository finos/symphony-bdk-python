from .suppression_listener import SuppressionListener
import logging
# A sample implementation of Abstract SuppressionListener class
# The listener can respond to incoming events if the respective event
# handler has been implemented


class SuppressionListenerImp(SuppressionListener):
    """Example implementation of Message Suppression Listener

        sym_bot_client: contains clients which respond to incoming events

    """

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client

    def on_message_suppression(self, suppressed_message):
        logging.debug('message suppression detected %s', suppressed_message)
