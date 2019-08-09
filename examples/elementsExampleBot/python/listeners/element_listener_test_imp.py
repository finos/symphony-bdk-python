import logging

#Import ElementsActionListener class from sym_api_client_python
#ElementsActionListener is an interface
#ElementsListenerTestImp implements this ElementsActionListener Interface
from sym_api_client_python.listeners.elements_listener import ElementsActionListener
#import ActionProcessor class --> contains functionality for handling form submission
from .action_processor import ActionProcessor



class ElementsListenerTestImp(ElementsActionListener):
    """Example implementation of ElementsActionListener

        sym_bot_client: contains clients which respond to incoming events

    """

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client

    def on_elements_action(self, action):
        msg_processor = ActionProcessor(self.bot_client, action)
