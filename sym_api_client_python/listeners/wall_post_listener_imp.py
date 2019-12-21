from .wall_post_listener import WallPostListener
import logging
# A sample implementation of Abstract WallPostListener class
# The listener can respond to incoming events if the respective event
# handler has been implemented


class WallPostListenerImp(WallPostListener):
    """Example implementation of WallPostListener

        sym_bot_client: contains clients which respond to incoming events

    """

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client

    def on_wall_post_msg(self, wall_post_msg):
        logging.debug('receieved incoming wall post %s', wall_post_msg)

    def on_shared_post(self, shared_post):
        logging.debug('received incoming shared post %s', shared_post)
