from .joke import JokeClient
import xml.etree.ElementTree as ET


class MessageProcessor:
    def __init__(self, bot_client):
        self.bot_client = bot_client

    def process(self, msg):
        msg_xml = msg['message']
        msg_root = ET.fromstring(msg_xml)
        msg_txt = msg_root[0].text

        if '/bot' in msg_txt and 'joke' in msg_txt:
            joke_client = JokeClient(self.bot_client)
            stream_id = msg['stream']['streamId']
            joke_client.send_joke(stream_id)
