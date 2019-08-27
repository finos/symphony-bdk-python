import xml.etree.ElementTree as ET
from ..processors.message_parser import MessageParser

class MessageProcessor:
    def __init__(self, bot_client):
        self.bot_client = bot_client
        self.message_parser = MessageParser()

    def process(self, msg):
        logging.debug('insdie of process')
        # msg_xml = msg['message']
        # msg_root = ET.fromstring(msg_xml)
        # msg_txt = msg_root[0].text
        msg_text = self.message_parser.get_text(msg)
        print('process')
        print(msg_txt)
        print('after')

        msg_to_send = dict(
                #message=msg_xml
                message='<messageML>Hello {}, hope you are doing well!</messageML>'.format(self.message_parser.get_im_firstname(msg))
                )


        if msg_txt:
            stream_id = self.message_parser.get_stream_id(msg)
            self.bot_client.get_message_client(). \
                    send_msg(stream_id, msg_to_send)
