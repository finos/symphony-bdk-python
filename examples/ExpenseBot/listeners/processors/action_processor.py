import xml.etree.ElementTree as ET
import logging
import base64
import json
from sym_api_client_python.processors.message_formatter import MessageFormatter
from sym_api_client_python.processors.sym_elements_parser import SymElementsParser
from ..expense_approval_form.expense_approval_class import expense_data, render_expense_approval_form, render_add_expense_form, render_remove_expense_form, upload_expense, remove_item
# from ..expense_approval_form.html import expense_approval_table.html
# from ..expense_approval_form.generate_expense_approval_table import generate_expense_approval_table, reeds_expense_form, generate_add_expense_form, generate_remove_expense_form


class ActionProcessor:

    def __init__(self, bot_client):
        self.bot_client = bot_client
        self.manager_submit = MessageFormatter().format_message('Expense Report has been approved')
        self.approve_expense_message = MessageFormatter().format_message('Your expense report has been approved')
        self.reject_expense_report = MessageFormatter().format_message('Your expense report has been rejected')

    def process_room_action(self, action):
        logging.debug('action_processor/room_process')
        logging.debug(json.dumps(action, indent=4))
        try:
            action_clicked = SymElementsParser().get_action(action)
            if action_clicked == 'approve-button':
                self.bot_client.get_message_client().send_msg(im_stream['id'], dict(message = '<messageML><mention uid="{}"/>Your Expense Report has been approved!</messageML>'.format(SymElementsParser().get_initiator_user_id(action))))
            elif action_clicked == 'reject-button':
                self.bot_client.get_message_client().send_msg(im_stream['id'], dict(message = '<messageML><mention uid="{}"/>Your Expense Report has been rejected.  Please reach out to your manager for further assistance.</messageML>'.format(SymElementsParser().get_initiator_user_id(action))))
            elif action_clicked == 'add-expense':
                self.bot_client.get_message_client().send_msg(im_stream['id'], dict(message = '<messageML><mention uid="{}"/></messageML>'.format(SymElementsParser().get_initiator_user_id(action))))
                self.bot_client.get_message_client().send_msg(im_stream['id'], render_add_expense_form('listeners/expense_approval_form/html/add_expense_form.html'))
            elif action_clicked == 'remove-expense':
                self.bot_client.get_message_client().send_msg(im_stream['id'], dict(message = '<messageML><mention uid="{}"/></messageML>'.format(SymElementsParser().get_initiator_user_id(action))))
                self.bot_client.get_message_client().send_msg(im_stream['id'], render_remove_expense_form('listeners/expense_approval_form/html/remove_expense.html'))
        except:
            raise

    def process_im_action(self, action):
        logging.debug('action_processor/im_process')
        logging.debug(json.dumps(action, indent=4))
        # self.im_stream = self.bot_client.get_stream_client().create_im([SymElementsParser().get_initiator_user_id(action)])
        if SymElementsParser().get_form_values(action)['action'] == 'add-expense-form':
            self.bot_client.get_message_client().send_msg(SymElementsParser().get_stream_id(action), render_add_expense_form('listeners/expense_approval_form/html/add_expense_form.html'))

        elif SymElementsParser().get_form_values(action)['action'] == 'add-expense-button':
            form_contents = SymElementsParser().get_form_values(action)
            upload_expense([(form_contents['add-vendor-textfield'], form_contents['add-date-textfield'], float(form_contents['add-price-textfield']))])
            self.bot_client.get_message_client().send_msg(SymElementsParser().get_stream_id(action), render_expense_approval_form('listeners/expense_approval_form/html/create_expense_approval_form.html'))

        elif SymElementsParser().get_form_values(action)['action'] == 'submit-expense':
            self.employee_id = SymElementsParser().get_initiator_user_id(action)
            self.employee_name = SymElementsParser().get_initiator_display_name(action)
            self.employee_stream = SymElementsParser().get_stream_id(action)

            self.manager_id = SymElementsParser().get_form_values(action)['person-selector']
            self.manager_username = self.bot_client.get_user_client().get_user_from_id(self.manager_id)['displayName']

            self.submit_message = MessageFormatter().format_message('Your expense has been submitted to {}'.format(self.manager_username))
            self.manager_recieve_message = MessageFormatter().format_message('{} submitted an expense report that needs your approval: '.format(self.employee_name))

            self.bot_client.get_message_client().send_msg(self.employee_stream, self.submit_message)
            self.im_stream = self.bot_client.get_stream_client().create_im(SymElementsParser().get_form_values(action)['person-selector'])

            self.bot_client.get_message_client().send_msg(self.im_stream['id'], self.manager_recieve_message)
            self.bot_client.get_message_client().send_msg(self.im_stream['id'], render_expense_approval_form('listeners/expense_approval_form/html/manager_expense_approval_form.html'))

        elif SymElementsParser().get_form_values(action)['action'] == 'approve-expense':
            self.manager_stream = SymElementsParser().get_stream_id(action)
            self.bot_client.get_message_client().send_msg(self.manager_stream, self.manager_submit)
            self.bot_client.get_message_client().send_msg(self.employee_stream, self.approve_expense_message)

        # elif SymElementsParser().get_form_values(action)['action'].startswith('remove-expense-button'):
        #     expense_number = int(SymElementsParser().get_form_values(action)['action'][-1])
        #     remove_item(expense_number)
        #     self.bot_client.get_message_client().send_msg(SymElementsParser().get_stream_id(action), self.removed_expense_message)
        #     self.bot_client.get_message_client().send_msg(self.room_stream, render_expense_approval_form('/Users/reed.feldman/Desktop/SDK/test/templateBots2/python/listeners/expense_approval_form/html/expense_approval_table.html'))
