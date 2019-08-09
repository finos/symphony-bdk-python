import xml.etree.ElementTree as ET
import logging
import base64
from sym_api_client_python.processors.message_formatter import MessageFormatter
from sym_api_client_python.processors.form_parser import FormParser
from .form import myform


class ActionProcessor:

    def __init__(self, bot_client, action):
        self.bot_client = bot_client
        self.action = action
        self.message_formatter = MessageFormatter()
        self.formParser = FormParser(action)
        self.process(self.action)

    def process(self, action):
        logging.debug('action_processor/process')
        stream = action['formStream']['streamId'].rstrip('=').replace('/', '_')
        self.msg_to_send = self.message_formatter.format_message('Your Form Submission has been recorded')
        self.bot_client.get_message_client().send_msg(stream, self.msg_to_send)
