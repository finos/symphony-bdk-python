import asyncio
import logging
from .im_listener import IMListener
from .simple_message_processor import MessageProcessor
from sym_api_client_python.processors.sym_message_parser import SymMessageParser




# A sample implementation of Abstract imListener class
# The listener can respond to incoming events if the respective event
# handler has been implemented


class IMListenerTestImp(IMListener):
    """Example implementation of IMListener

        sym_bot_client: contains clients which respond to incoming events

    """

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client

    def on_im_message(self, im_message):
        logging.debug('message received in IM')
        msg_processor = MessageProcessor(self.bot_client)
        msg_processor.process(im_message)

    def on_im_created(self, im_created):
        logging.debug('IM created!', im_created)

class AsyncIMListenerImp(IMListener):
    """Example implementation of IMListener with asynchronous functionality

    Call the bot with /wait to see an example of a non-blocking wait

    """

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client
        self.message_parser = SymMessageParser()

    async def on_im_message(self, msg):
        logging.debug('message received in IM', msg)


        msg_text = self.message_parser.get_text(msg)

        if "/wait" in msg_text:
            await asyncio.sleep(5)
            msg_to_send = dict(
                    message='<messageML>Hello {}, sorry to keep you waiting!</messageML>'.format(
                        self.message_parser.get_im_first_name(msg))
                    )
        else:
            msg_to_send = dict(
                    message='<messageML>Hello {}, hope you are doing well!</messageML>'.format(
                        self.message_parser.get_im_first_name(msg))
                    )

        if msg_text:
            stream_id = self.message_parser.get_stream_id(msg)
            self.bot_client.get_message_client(). \
                    send_msg(stream_id, msg_to_send)


    async def on_im_created(self, im_created):
        logging.debug("IM created!", im_created)
