import xml.etree.ElementTree as ET
import logging
from sym_api_client_python.processors.message_formatter import MessageFormatter


class MessageProcessor:
    def __init__(self, bot_client, msg):
        self.bot_client = bot_client
        self.msg = msg
        self.message_formatter = MessageFormatter()
        self.process(self.msg)

    #reads message and processes it
    #look inside logs/example.log to see the payload (metadata representing event coming over the datafeed)
    def process(self, msg):
        msg_xml = msg['message']
        msg_root = ET.fromstring(msg_xml)
        self.msg_txt = msg_root[0].text
        #format message to send in MessageML see: https://developers.symphony.com/symphony-developer/docs/messagemlv2
        self.help_message = self.message_formatter.format_message('Command List: ' + '/expense : showcases expense approval form')
        self.default_message = self.message_formatter.format_message('type /help to list commands')
        #access send_msg() function in sym_api_client_python
        #see symphony-api-client-python/sym_api_client_python/clients/message_client.py for full reference
        #send_msg takes two params, stream and message.  We grab stream from message coming in
        if self.msg_txt.startswith('/help'):
            self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], self.help_message)
        else:
            self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], self.default_message)
