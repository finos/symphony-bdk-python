
class Form:

    """
    To start using Symphony Elements, you first need to create a form using the
    Form element. This represents all the information of the elements present
    in the form to be sent to the datafeed.  The available elements are Buttons,
    Text Field, Text Area, Checkbox, Radio Button, Dropdown Menu, Person Selector,
    and Table Select.

    The following form contains setter functions corresponding to each element.

    To create a form, instantiate the Form Class with a unique form id.  Add elements
    to this form by calling the appropriate function in the Form Class.
    """

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
        set_header('Form Title', 'h4') --> <h4>Form title</h4>

        This function sets a header on the Form Element.
        Users must specify the text and size of the header that
        they wish to create.
        """
        header = (size,text)
        self.headers.append(header)

    def add_button_to_form(self, name, text, type='action'):
        """
        add_button_to_form('test-button', 'Click Me!', 'action') --> <button name="test-button" type="action">Click Me!</button>

        This function adds a button to the Form Element.
        Users must specify the name, button text, and type.
        If no type is given, it's type will be set by default to 'action'
        """
        button = (name, type, text)
        self.buttons.append(button)


    def add_text_field_to_form(self, name, text, placeholder='', required='true', maxlength=128, minlength=1):
        """
        add_text_field_to_form('id1', 'Input some text...') --> <text-field name="id1" placeholder="" required="true" maxlength="128" minlength="1">Input some text...</text-field>

        This function adds a text field to a Form Element.
        Users must specifiy a name, display text, and/or optional parameters placeholder,
        required, maxlength, and minlength.
        """
        text_field = (name, placeholder, required, maxlength, minlength, text)
        self.text_fields.append(text_field)

    def add_masked_text_field_to_form(self, name, text, placeholder='', required='true', masked='true', maxlength = 128, minlength=1):
        """
        add_masked_text_field_to_form('id1', 'Input some text...') --> <text-field name="id1" placeholder="" required="true" masked="true" maxlength="128" minlength="1">Input some text...</text-field>

        This function adds a masked text field to a Form Element.
        Users must specifiy a name and text and/or optional parameters placeholder, masked,
        required, maxlength, and minlength.
        Set masked='true' in order to create a masked text field.
        """
        masked_text_field = (name, placeholder, required, masked, maxlength, minlength, text)
        self.masked_text_fields.append(masked_text_field)

    def add_text_area_to_form(self, name, text, placeholder='', required='true'):
        """
        add_text_area_to_form('id', 'My name is..') --> <textarea name="id" placeholder="" required="true">My name is..</textarea>

        This function adds a text area to a Form Element.
        Users must specifiy name, text and/or optional parameters, placeholder,
        and required.
        """
        text_area = (name, placeholder, required, text)
        self.text_areas.append(text_area)

    def add_check_box_to_form(self, name, text, value='on', checked='false'):
        """
        myform.add_check_box_to_form('id1', 'Check Me!') --> <checkbox name="id1" value="on" checked="false">Check Me!</checkbox>

        This function adds a checkbox to a Form Element.
        Users must specify name, text, and/or optional parameters checked and value.
        Set checked='true' in order to have checkbox appear checked upon sending.
        """
        check_box = (name, value, checked, text)
        self.check_boxes.append(check_box)

    def add_radio_button_to_form(self, name, text, value='on', checked='false'):
        """
        add_radio_button_to_form('id1', 'Click Me!') --> <radio name="id1" value="on" checked="false">Click Me!</radio>

        This function adds a radio button to a Form Elment.
        Users must specify name, text, and/or optional parameters checked and value.
        Set checked='true' in order to have radio appear selected upon sending.
        """
        radio_button = (name, value, checked, text)
        self.radio_buttons.append(radio_button)

    def add_dropdown_menu_to_form(self, dropdown_group):
        """
        add_dropdown_menu_to_form([('dropdown', 'false', 'value1', 'false', 'Reeds Option'),
                                   ('dropdown', 'false', 'value2', 'false', 'Reeds Option2'),
                                   ('dropdown', 'false', 'value3', 'false', 'Reeds Option3')])

         --> <select name="dropdown" required="false">
               <option value="value1" selected="false">Reeds Option</option>
               <option value="value2" selected="false">Reeds Option2</option>
               <option value="value3" selected="false">Reeds Option3</option>
             </select>

        This function adds a dropdown menu to the Form Element.
        Users must specify a dropdown_group as a list of tuple's corresponding to each dropdown element.
        The dropdown group parameter must follow the following tuple pattern:

        (parent_name, required, value, selected, text)

        Users should pass a list of these tuples in order to create a dropdown group
        as shown above.
        """

        self.dropdown_menu_groups.append(dropdown_group)

    def add_person_selector_to_form(self, name, placeholder='', required='false'):
        """
        add_person_selector_to_form('awesome-users', 'enter names...') --> <person-selector name="awesome-users" placeholder="enter names..." required="false" />

        This function adds a person selector to the Form Element.
        Users must specify a name and/or optional parameters placeholder and required
        When a user is selected, the corresponding user_id is stored in an
        array corresponding to the name parameter
        """
        person_selector = (name, placeholder, required)
        self.person_selectors.append(person_selector)

    def add_table_selector_to_form(self, position, type, type_name, header_list, body_list, footer_list):
        """
        add_table_selector_to_form('left', 'checkbox', 'table-box',
                                    ['H1', 'H2', 'H3'],
                                    [["A1", "B1", "C1"],["A2", "B2", "C2"], ["A3", "B3", "C3"]],
                                    ["F1","F2","F3"])

        -->  <table>
              <thead>
                <tr>
                  <td>
                    <input type="checkbox" name="table-header" />
                  </td>
                  <td>H1</td>
                  <td>H2</td>
                  <td>H3</td>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <input type="checkbox" name="table-box1" />
                  </td>
                  <td>A1</td>
                  <td>B1</td>
                  <td>C1</td>
                </tr>
                <tr>
                  <td>
                    <input type="checkbox" name="table-box2" />
                  </td>
                  <td>A2</td>
                  <td>B2</td>
                  <td>C2</td>
                </tr>
                <tr>
                  <td>
                    <input type="checkbox" name="table-box3" />
                  </td>
                  <td>A3</td>
                  <td>B3</td>
                  <td>C3</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td>
                    <input type="checkbox" name="table-footer" />
                  </td>
                  <td>F1</td>
                  <td>F2</td>
                  <td>F3</td>
                </tr>
              </tfoot>
            </table>

        This function adds a table selector to the Form Element.
        Users must specify a position, type, type_name, header_list, body_list, and footer list.

        position: 'left' or 'right',
        type: 'checkbox' or 'button'

        """
        table_selector = (position, type, type_name, header_list, body_list, footer_list)
        self.table_selectors.append(table_selector)
