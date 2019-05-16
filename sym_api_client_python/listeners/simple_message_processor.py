import xml.etree.ElementTree as ET


class MessageProcessor:
    def __init__(self, bot_client):
        self.bot_client = bot_client

    def process(self, msg):
        msg_xml = msg['message']
        msg_root = ET.fromstring(msg_xml)
        msg_txt = msg_root[0].text

        msg_to_send = dict(
                #message=msg_xml
                message='<messageML>Simple response!</messageML>'
                )

        print(msg_txt)
        print(msg_to_send)

        if msg_txt:
            stream_id = msg['stream']['streamId']
            self.bot_client.get_message_client(). \
                    send_msg(stream_id, msg_to_send)
           

