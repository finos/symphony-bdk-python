import logging

#Import IMListener class from SDK
#IMListener is an interface
#IMListenerTestImp implements this IMListener Interface
from sym_api_client_python.listeners.im_listener import IMListener
#import MessageProcessor class --> parses message/handles functionality
from .processors.im_processor import IMProcessor



class IMListenerTestImp(IMListener):
    """Example implementation of IMListener

        sym_bot_client: contains clients which respond to incoming events

    """

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client

    #function gets called everytime bot hears a message in an IM
    def on_im_message(self, im_message):
        #MessageProcessor class holds specific room creation functionality
        #Initialize MessageProcessor class
        msg_processor = IMProcessor(self.bot_client, im_message)

    #function gets called everytime IM message is sent/created to bot
    def on_im_created(self, im_created):
        logging.debug('IM created!', im_created)
