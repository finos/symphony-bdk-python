import xml.etree.ElementTree as ET
import logging
import base64
import json
from sym_api_client_python.processors.message_formatter import MessageFormatter
from sym_api_client_python.processors.form_parser import FormParser
from ..expense_approval_form.expense_approval_class import expense_data, render_expense_approval_form, render_add_expense_form, render_remove_expense_form, upload_expense, remove_item

class ActionProcessor:

    def __init__(self, bot_client):
        self.bot_client = bot_client
        self.add_expense_message = MessageFormatter().format_message('Your expense has been added')
        self.removed_expense_message = MessageFormatter().format_message('Your expense has been removed')
        self.approve_expense_message = MessageFormatter().format_message('Your expense report has been approved')
        self.reject_expense_report = MessageFormatter().format_message('Your expense report has been rejected')

    def process_room_action(self, action):
        logging.debug('action_processor/room_process')
        logging.debug(json.dumps(action, indent=4))
        self.room_stream = FormParser().get_stream_id(action)
        im_stream = self.bot_client.get_stream_client().create_im([FormParser().get_initiator_userId(action)])
        try:
            action_clicked = FormParser().get_action(action)
            if action_clicked == 'approve-button':
                self.bot_client.get_message_client().send_msg(im_stream['id'], dict(message = '<messageML><mention uid="{}"/>Your Expense Report has been approved!</messageML>'.format(FormParser().get_initiator_userId(action))))
            elif action_clicked == 'reject-button':
                self.bot_client.get_message_client().send_msg(im_stream['id'], dict(message = '<messageML><mention uid="{}"/>Your Expense Report has been rejected.  Please reach out to your manager for further assistance.</messageML>'.format(FormParser().get_initiator_userId(action))))
            elif action_clicked == 'add-expense':
                self.bot_client.get_message_client().send_msg(im_stream['id'], dict(message = '<messageML><mention uid="{}"/></messageML>'.format(FormParser().get_initiator_userId(action))))
                self.bot_client.get_message_client().send_msg(im_stream['id'], render_add_expense_form('/html/add_expense_form.html'))
            elif action_clicked == 'remove-expense':
                self.bot_client.get_message_client().send_msg(im_stream['id'], dict(message = '<messageML><mention uid="{}"/></messageML>'.format(FormParser().get_initiator_userId(action))))
                self.bot_client.get_message_client().send_msg(im_stream['id'], render_remove_expense_form('/html/remove_expense.html'))
        except:
            raise

    def process_im_action(self, action):
        logging.debug('action_processor/im_process')
        logging.debug(json.dumps(action, indent=4))
        if FormParser().get_form_values(action)['action'] == 'add-expense-button':
            form_contents = FormParser().get_form_values(action)
            upload_expense([(form_contents['add-vendor-textfield'], form_contents['add-date-textfield'], float(form_contents['add-price-textfield']))])
            self.bot_client.get_message_client().send_msg(FormParser().get_stream_id(action), self.add_expense_message)
            self.bot_client.get_message_client().send_msg(self.room_stream, render_expense_approval_form('/html/expense_approval_table.html'))
        elif FormParser().get_form_values(action)['action'].startswith('remove-expense-button'):
            expense_number = int(FormParser().get_form_values(action)['action'][-1])
            remove_item(expense_number)
            self.bot_client.get_message_client().send_msg(FormParser().get_stream_id(action), self.removed_expense_message)
            self.bot_client.get_message_client().send_msg(self.room_stream, render_expense_approval_form('/html/expense_approval_table.html'))
