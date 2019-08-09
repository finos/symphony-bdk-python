#IMPORT FormClient Class from sym_api_client_python
from sym_api_client_python.clients.form_client import FormClient


#CREATE AN INSTANCE OF FormClient:
myform = FormClient('reed_form')
myform.set_header('My Object', 'h4')
myform.add_button_to_form('Button1', 'Button1', 'action')
myform.add_button_to_form('Button2', 'Button2', 'action')
myform.add_text_field_to_form('textfield-id', 'Input some text...')
myform.add_masked_text_field_to_form('masked-id', 'Input some text...')
myform.add_text_area_to_form('textarea-id', 'My name is..')
myform.add_check_box_to_form('check-id', 'Check Me!')
myform.add_radio_button_to_form('radio-id', 'Click Me!')
myform.add_dropdown_menu_to_form([('dropdown', 'false', 'value1', 'false', 'Reeds Option'),
                                     ('dropdown', 'false', 'value2', 'false', 'Reeds Option2'),
                                     ('dropdown', 'false', 'value3', 'false', 'Reeds Option3')])
myform.add_person_selector_to_form('awesome-users', 'enter names...')
myform.add_table_selector_to_form('left', 'checkboxes', 'table-box', ['H1', 'H2', 'H3'], [["A1", "B1", "C1"],
                                                                            ["A2", "B2", "C2"],
                                                                    ["A3", "B3", "C3"]], ["F1","F2","F3"])
