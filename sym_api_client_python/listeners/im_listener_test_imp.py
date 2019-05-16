from .im_listener import IMListener
from .simple_message_processor import MessageProcessor
import logging
# A sample implementation of Abstract imListener class
# The listener can respond to incoming events if the respective event
# handler has been implemented


class IMListenerTestImp(IMListener):
    """Example implementation of IMListener

        sym_bot_client: contains clients which respond to incoming events

    """

    def __init__(self, sym_bot_client):
        self.botClient = sym_bot_client
        
    def on_im_message(self, im_message):
        logging.debug('message received in IM', im_message)
        msg_processor = MessageProcessor(self.bot_client)
        msg_processor.process(im_message)
        
    def on_im_created(self, im_created):
        logging.debug('IM created!', im_created)
