import xml.etree.ElementTree as ET
import logging
import json
from sym_api_client_python.processors.message_formatter import MessageFormatter
from sym_api_client_python.processors.sym_message_parser import SymMessageParser
from ..expense_approval_form.expense_approval_class import expense_data, render_expense_approval_form, upload_expense, remove_item

class RoomProcessor:

    def __init__(self, bot_client):
        self.bot_client = bot_client
        self.message_formatter = MessageFormatter()
        self.sym_message_parser = SymMessageParser()
        #hard code to the userId of bot you are using.
        self.bot_id = '349026222344891'
        self.default_message = self.default_message = self.message_formatter.format_message('type @karlPythonDemo help to view commands')

    def process_room_message(self, msg):
        logging.debug('room_processor/process_room_message()')
        logging.debug(json.dumps(msg, indent=4))
        self.help_message = dict(message = """<messageML>
                                    <h2>This is an demo of how to create, update, and submit an expense form using Symphony Elements</h2>
                                    <p>Type @karlPythonDemo expense to view expense approval form</p>
                                              </messageML>
                            """)

        mentioned_users = self.sym_message_parser.get_mention_ids(msg)
        commands = self.sym_message_parser.get_text(msg)

        if mentioned_users:
            if mentioned_users[0] == self.bot_id and commands[0] == 'help':
                print('in room')
                self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], self.help_message)
            if mentioned_users[0] == self.bot_id and commands[0] == 'expense':
                self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], render_expense_approval_form('listeners/expense_approval_form/html/expense_approval_table.html'))

        else:
            self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], self.default_message)
