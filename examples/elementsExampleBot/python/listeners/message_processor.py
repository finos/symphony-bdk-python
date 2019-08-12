import xml.etree.ElementTree as ET
import logging
#IMPORT MessageFormatter Class from sym_api_client_python
from sym_api_client_python.processors.message_formatter import MessageFormatter
#IMPORT instance of Form Object (myform) from form.py
from .form import myform


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
        self.msg_to_send = self.message_formatter.format_message('Hello ' + self.msg['user']['firstName']  + ' , you entered: ' +self.msg_txt)
        self.help_message = self.message_formatter.format_message('Command List: ' + '/createroom [roomname] : creates room with roomname')

        #PROCESS FORM OBJECT AND FORMAT SO THAT ITS A MESSAGEML OBJECT
        #AS A MESSAGEML OBJECT, USERS CAN SEND IT AS A MESSAGE
        self.elements_message = myform.format_element()
        self.default_message = self.message_formatter.format_message('type /help to list commands')
        #access send_msg() function in sym_api_client_python
        #see symphony-api-client-python/sym_api_client_python/clients/message_client.py for full reference
        #send_msg takes two params, stream and message.  We grab stream from message coming in
        if self.msg_txt.startswith('/createroom'):
            self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], self.msg_to_send)
            self.create_room(msg)
        elif self.msg_txt.startswith('/help'):
            self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], self.help_message)
        elif self.msg_txt.startswith('/elements'):
            self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], self.elements_message)
        else:
            self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], self.default_message)

    def create_room(self, message):

        self.second_word = self.msg_txt.split(' ')[1]
        print(self.second_word)
        #see create_room() inside of symphony-api-client-python/sym_api_client_python/clients/stream_client.py for full reference
        room_obj = {
            "name": self.second_word,
            "description": 'Created by pyBot',
            "keywords": [],
            "membersCanInvite": True,
            "discoverable": True,
            "public": True,
            "readOnly": False,
            "copyProtected": False,
            "crossPod": False,
            "viewHistory": True,
            "multiLateralRoom": False,
        }
        msg_to_send = self.message_formatter.format_message('chatRoomCreated ' + room_obj['name'])
        fail_msg = self.message_formatter.format_message('chatroom with same name already exists!')

        try:
            self.bot_client.get_stream_client().create_room(room_obj)
            logging.debug('room created')
            self.bot_client.get_message_client().send_msg(message['stream']['streamId'], msg_to_send)
        except APIClientErrorException:
            self.bot_client.get_message_client().send_msg(message['stream']['streamId'], fail_msg)
