import xml.etree.ElementTree as ET
import logging

#IMPORT MessageFormatter and FormParser classes from sym_api_client_python
from sym_api_client_python.processors.message_formatter import MessageFormatter
from sym_api_client_python.processors.form_parser import FormParser

#IMPORT myform object from form.py
from .form import myform


class ActionProcessor:
    """
    ActionProcessor Class does some custom processing using MessageFormatter and
    Form Parser helper classes.  ActionProcessor takes bot_client and action as
    parameters.  In this case action is a json payload representing the action event
    that is dispatched after a user submitted a form.
    """

    def __init__(self, bot_client, action):
        self.bot_client = bot_client
        self.action = action
        self.message_formatter = MessageFormatter()
        #pass action object into FormParser so user can easily access its attributes
        self.formParser = FormParser(action)
        self.process(self.action)

    def process(self, action):
        logging.debug('action_processor/process')
        #Example of parsing the action to get stream_id
        stream = self.formParser.get_form_stream_id()
        #grab values submitted in the form
        print(self.formParser.get_form_values())
        #send user message that the form submission has been recorded
        self.msg_to_send = self.message_formatter.format_message('Your Form Submission has been recorded')
        self.bot_client.get_message_client().send_msg(stream, self.msg_to_send)
