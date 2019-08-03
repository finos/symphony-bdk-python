import json
from yattag import Doc

class Form:

    def __init__(self, form_id):
        self.form_id = form_id
        self.headers = []
        self.buttons = []
        self.text_fields = []
        self.masked_text_fields = []
        self.text_areas = []
        self.check_boxes = []
        self.radio_buttons = []
        self.dropdown_menu_groups = []
        self.person_selectors = []
        self.table_selectors = []

    def set_header(self, text, size):
        """
        This function sets an optional header for the form element
        Users can specify the text and size of the header that
        they wish to create.
        """
        header = (size,text)
        self.headers.append(header)

    def add_button_to_form(self, name, text, button_type='action'):
        """
        This function adds a button to a form element.
        Users must specify the name and type.
        If no type is given, it's type will be set by default to 'action'
        """
        button = (name, button_type, text)
        self.buttons.append(button)


    def add_text_field_to_form(self, name, text, placeholder='', required='true', maxlength=100, minlength=0):
        """
        This function adds a text field to a form element.
        Users must specifiy a name and/or optional parameters placeholder,
        required, maxlength, and minlength
        """
        text_field = (name, placeholder, required, maxlength, minlength, text)
        self.text_fields.append(text_field)

    def add_masked_text_field_to_form(self, name, text, placeholder='', required='true', masked='true', maxlength = 100, minlength=0):
        """
        This function adds a masked text field to a form.
        Users must specifiy a name and/or optional parameters placeholder, masked,
        required, maxlength, and minlength.
        Set masked='true' in order to create a masked text field.
        """
        masked_text_field = (name, placeholder, required, masked, maxlength, minlength, text)
        self.masked_text_fields.append(masked_text_field)

    def add_text_area_to_form(self, name, text, placeholder='', required='true'):
        """
        This function adds a text area to a form.
        Users must specifiy a name, text, and optional parameters, placeholder,
        and required.
        """
        text_area = (name, placeholder, required, text)
        self.text_areas.append(text_area)

    def add_check_box_to_form(self, name, text, value='on', checked='false'):
        """
        This function adds a checkbox to a form element.
        Users must specify a name, value, text, and an optional checked parameter.
        text parameter is the what appears on the checkbox in Symphony client.
        If checked is set='true', the button appears to be checked
        """
        check_box = (name, value, checked, text)
        self.check_boxes.append(check_box)

    def add_radio_button_to_form(self, name, text, value='on', checked='false'):
        """
        This function adds a radio button to a form element
        Users must specify a name, value, checked and text.
        If the user does not pass a parameter to value or checked, they
        will be set to on and false respectively.
        text text parameter is the what appears on the button in Symphony client.
        """
        radio_button = (name, value, checked, text)
        self.radio_buttons.append(radio_button)

    def add_dropdown_menu_to_form(self, dropdown_group):
        """
        This function creates a group of dropdown elements and adds it to a form element
        To invoke this function, pass a list of tuples.  Each tuple represents
        a group of dropdowns, including parent, required, value, selected, and text.

        An example dropdown group list follows the tuple pattern:

        (parent name, required, value, selected, text)

        [('dropdown1', 'false', 'value1', 'true', 'Reeds Option'),
         ('dropdown1', 'false', 'value2', 'false', 'Reeds Option2'),
         ('dropdown1', 'false', 'value3', 'false', 'Reeds Option3')]
        """

        self.dropdown_menu_groups.append(dropdown_group)

    def add_person_selector_to_form(self, name, placeholder='', required='false'):
        """
        This function adds a person selector to the form element
        Users must specify a name and optional parameters placeholder and required
        When a user is selected, the corresponding user_id is stored in an
        array corresponding to the name parameter
        """
        person_selector = (name, placeholder, required)
        self.person_selectors.append(person_selector)

    def add_table_selector_to_form(self, position, type, header_list, body_list, footer_list):
        """
        This function adds a table selector to the form element
        Users must specify a type (button or checkbox) and position (left or right)
        Users must also pass a data json object representing the header,
        body, and footer data corresponding to this table.

        """
        table_selector = (position, type, header_list, body_list, footer_list)
        self.table_selectors.append(table_selector)


    def create_message_ML(self):
        doc, tag, text, line = Doc().ttl()
        with tag('messageML'):
            with tag('form', id = self.form_id):
                with tag(self.headers[0][0]):
                    text(self.headers[0][1])
                for i, j, k in self.buttons:
                    with tag('button', name=i, button_type=j):
                        text(k)
                for i,j,k,l,m,n in self.text_fields:
                    with tag('text-field', name=i, placeholder=j, required=k, maxlength=l, minlength=m):
                        text(n)
                for i,j,k,l,m,n,o in self.masked_text_fields:
                    with tag('text-field', name=i, placeholder=j, required=k, masked=l, maxlength=m, minlength=n):
                        text(o)
                for i,j,k,l in self.text_areas:
                    with tag('textarea', name=i, placeholder=j, required=k):
                        text(l)
                for i,j,k,l in self.check_boxes:
                    with tag('checkbox', name=i, placeholder=j, required=k):
                        text(l)
                for i,j,k,l in self.radio_buttons:
                    with tag('radio', name=i, placeholder=j, required=k):
                        text(l)
                for i in self.dropdown_menu_groups:
                    with tag('select', name=i[0][0], required=i[0][3]):
                        for j in i:
                            with tag('option', value=j[2], selected=j[1]):
                                text(j[4])
                for i, j, k in self.person_selectors:
                    doc.stag('person-selector', name=i, placeholder=j, required=k)

                with tag('table'):
                    with tag('thead'):
                        with tag('tr'):
                            doc.stag('td', 'Select')
                            for i in self.table_selectors:
                                for j in i[2]:
                                    doc.stag('td', j)

                    with tag('tbody'):
                            for i in self.table_selectors:
                                    for j in i[3]:
                                        with tag('tr'):
                                            for k in j:
                                                doc.stag('td', k)

                    with tag('tfoot'):
                            for i in self.table_selectors:
                                with tag('tr'):
                                    for j in i[4]:
                                        doc.stag('td', j)


            print(doc.getvalue())


myform = Form('reed_form')
myform.set_header('My Object', 'h4')
myform.add_button_to_form('reed', 'Button1', 'action')
myform.add_button_to_form('karl', 'Button2', 'action')
myform.add_text_field_to_form('id1', 'Input some text...')
myform.add_masked_text_field_to_form('id1', 'Input some text...')
myform.add_text_area_to_form('id', 'My name is..')
myform.add_check_box_to_form('id1', 'Check Me!')
myform.add_radio_button_to_form('id1', 'Click Me!')
myform.add_dropdown_menu_to_form([('dropdown', 'false', 'value1', 'false', 'Reeds Option'),
                                     ('dropdown', 'false', 'value2', 'false', 'Reeds Option2'),
                                     ('dropdown', 'false', 'value3', 'false', 'Reeds Option3')])
myform.add_person_selector_to_form('awesome-users', 'enter names...')
myform.add_table_selector_to_form('left', 'button', ['H1', 'H2', 'H3'], [["A1", "B1", "C1"],
                                                                            ["A2", "B2", "C2"],
                                                                    ["A3", "B3", "C3"]], ["F1","F2","F3"])
myform.create_message_ML()

# data = json.dumps({"data" : self.__dict__})
# print(data)
#USE YATTAG TO CREATE MESSAGEML ELEMENT/FORM OBJECT:
