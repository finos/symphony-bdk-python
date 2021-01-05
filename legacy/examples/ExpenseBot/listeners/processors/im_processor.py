import logging
import json
from sym_api_client_python.processors.message_formatter import MessageFormatter
from sym_api_client_python.processors.sym_message_parser import SymMessageParser
from ..expense_approval_form.expense_approval_class import expense_data, render_expense_approval_form, upload_expense, remove_item



class IMProcessor:
    def __init__(self, bot_client, msg):
        self.bot_client = bot_client
        self.msg = msg
        self.bot_id = '349026222344891'
        self.message_formatter = MessageFormatter()
        self.sym_message_parser = SymMessageParser()
        self.process(self.msg)

    #reads message and processes it
    #look inside logs/example.log to see the payload (metadata representing event coming over the datafeed)
    def process(self, msg):
        logging.debug('im_processor/process_im_message()')
        logging.debug(json.dumps(msg, indent=4))
        self.help_message = dict(message = """<messageML>
                                    <h3>Use ExpenseBot to create, update, and submit an expense form using Symphony Elements</h3>
                                    <p>Type @karlPythonDemo <b>'create expense'</b> to create an expense approval form</p>
                                    <p>In order to assign your expense approval form to your manager, you must first add an expense</p>
                                              </messageML>
                            """)

        mentioned_users = self.sym_message_parser.get_mention_ids(msg)
        commands = self.sym_message_parser.get_text(msg)

        if mentioned_users:
            if mentioned_users[0] == self.bot_id and commands[0] == 'help':
                self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], self.help_message)

            elif mentioned_users[0] == self.bot_id and commands[0] == 'create' and commands[1] == 'expense':
                expense_data['ExpenseApprovalForm']['person_name'] = self.sym_message_parser.get_im_name(msg)
                self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], render_expense_approval_form('listeners/expense_approval_form/html/create_expense_approval_form.html'))

            else:
                print('catching else')
                self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], self.help_message)
        else:
            self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], self.help_message)
