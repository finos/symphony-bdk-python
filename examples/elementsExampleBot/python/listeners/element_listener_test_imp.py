import logging

#Import IMListener class from SDK
#IMListener is an interface
#IMListenerTestImp implements this IMListener Interface
from sym_api_client_python.listeners.elements_listener import ElementsActionListener
#import MessageProcessor class --> parses message/handles functionality
from .action_processor import ActionProcessor



class ElementsListenerTestImp(ElementsActionListener):
    """Example implementation of IMListener

        sym_bot_client: contains clients which respond to incoming events

    """

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client

    def on_elements_action(self, action):
        msg_processor = ActionProcessor(self.bot_client, action)
