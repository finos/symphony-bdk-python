#IMPORT FormClient Class from sym_api_client_python
from sym_api_client_python.clients.form_client import FormClient


#CREATE AN INSTANCE OF FormClient:
myform = FormClient('reed_form')
myform.add_header('Full Name', 'h1')
myform.add_text_field_to_form('text-field-id', 'Type Your Full Name...')
myform.add_header('Authentication Key', 'h6')
myform.add_masked_text_field_to_form('masked-id', 'Authentication Key')
myform.add_header('Select your country', 'h4')
myform.add_dropdown_menu_to_form([('country', 'true', 'value1', 'false', 'Brazil'),
                                  ('country', 'false', 'value2', 'false', 'United States'),
                                  ('country', 'false', 'value3', 'false', 'China')])
myform.add_header('Select a Person', 'h4')
myform.add_person_selector_to_form('awesome-users', 'Enter Names...')
myform.add_header('Send a Comment', 'h4')
myform.add_text_area_to_form('textarea-id', 'Type Something...')
myform.add_header('Choose one option', 'h4')
myform.add_radio_button_to_form('radio-id', 'Enabled selected')
myform.add_radio_button_to_form('radio-id2', 'Enabled unselected')
myform.add_header('Choose one option', 'h4')
myform.add_check_box_to_form('check-id', 'Enabled checked')
myform.add_check_box_to_form('check-id2', 'enabled unchecked')

myform.add_button_to_form('reset-button', 'Reset', 'reset')
myform.add_button_to_form('submit-button', 'Submit', 'action')
# myform.add_header('Table Select', 'h3')
# myform.add_table_selector_to_form('left', 'checkbox', 'table-box',
#                             ['H1', 'H2', 'H3'],
#                             [["A1", "B1", "C1"],["A2", "B2", "C2"], ["A3", "B3", "C3"]],
#                             ["F1","F2","F3"])
