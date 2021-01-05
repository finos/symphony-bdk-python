from .elements_listener import ElementsActionListener
import logging


# A sample implementation of Abstract imListener class
# The listener can respond to incoming events if the respective event
# handler has been implemented


class ElementsListenerTestImp(ElementsActionListener):
    """Example implementation of ElementsActionListener

        sym_bot_client: contains clients which respond to incoming events

    """

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client

    def on_elements_action(self, action):
        logging.debug('element submitted :')


class AsyncElementsListenerTestImp(ElementsActionListener):
    """Example implementation of ElementsListener with asynchronous functionality"""

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client

    async def on_elements_action(self, action):
        logging.debug('async element submitted :')
