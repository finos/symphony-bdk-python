from yattag import Doc


class FormBuilder:
    """
    To start using Symphony Elements, you first need to create a form using the
    FormClient class.  The available elements can be found here: https://developers.symphony.com/symphony-developer/docs/available-components

    The following form contains setter functions corresponding to each element.

    To create a form, instantiate the FormBuilder class with a unique form id.  Add elements
    to this form by calling the appropriate setter function in the Form Class.

    Using this class allows a user to generate a messageML object corresponding to the elements inside the form.
    When this object is instantiated, it creates an empty string.  With every method called, the empty string is appended
    with messageML corresponding to the symphony element.  Lastly, users must call the format_element method in order to
    wrap the messageML string with the appropriate <messageML> tags.  At this point, the object can be sent as a message
    inside of Symphony.

    See examples/elementsExampleBot/form.py and examples/elementsExampleBot/message_processor.py for example usage:  
    """

    def __init__(self, form_id):
        self.form_id = form_id
        self.messageML = ''

    def format_element(self):
        """
        create_messageML() takes in a form object, parses its attritubes/metadata and returns
        a dictionary: {message : messageML object}.  This is the correct format to send
        in the Create Message v4 REST call.

        This messageML object is bootstrapped properly with <form> and
        <messageML> tags so that it can be rendered as an Element as is.
        """

        return dict(message='<messageML>' +
                            '<form id="{}">'.format(self.form_id)
                            + self.messageML +
                            '</form>'
                            '</messageML>')

    def add_header(self, text, size):
        """
        This function sets a header on the Form Element.
        Users must specify the text and size of the header that
        they wish to create.

        Returns a header: <h4>Form title</h4>
        """
        header = (size, text)
        doc, tag, text, line = Doc().ttl()
        with tag(header[0]):
            text(header[1])

        self.messageML += doc.getvalue()

    def add_button(self, name, display, type='action'):
        """
        This function adds a button to the Form Element.
        Users must specify the name, button text, and type.
        If no type is given, it's type will be set by default to 'action'

        Returns a button: <button name="test-button" type="action">Click Me!</button>
        """
        button = (name, type, display)
        doc, tag, text, line = Doc().ttl()
        with tag('button', name=name, type=type):
            text(display)

        self.messageML += doc.getvalue()

    def add_text_field(self, name, display, placeholder='', required='true', masked='true', maxlength=128, minlength=1):
        """
        This function adds a text field to a Form Element.
        Users must specifiy a name, display text, and/or optional parameters placeholder,
        required, maxlength, and minlength.

        Returns a text field: <text-field name="id1" placeholder="" required="true" maxlength="128" minlength="1">Input some text...</text-field>
        """
        doc, tag, text, line = Doc().ttl()

        with tag('text-field', name=name, placeholder=placeholder, required=required, masked=masked,
                 maxlength=maxlength, minlength=minlength):
            text(display)

        self.messageML += doc.getvalue()

    def add_text_area(self, name, display, placeholder='', required='true'):
        """
        This function adds a text area to a Form Element.
        Users must specifiy name, text and/or optional parameters, placeholder,
        and required.

        Returns a text area: <textarea name="id" placeholder="" required="true">My name is..</textarea>
        """
        doc, tag, text, line = Doc().ttl()
        with tag('textarea', name=name, placeholder=placeholder, required=required):
            text(display)

        self.messageML += doc.getvalue()

    def add_check_box(self, name, display, value='on', checked='false'):
        """
        This function adds a checkbox to a Form Element.
        Users must specify name, text, and/or optional parameters checked and value.
        Set checked='true' in order to have checkbox appear checked upon sending.

        Returns a checkbox: <checkbox name="id1" value="on" checked="false">Check Me!</checkbox>
        """
        doc, tag, text, line = Doc().ttl()

        with tag('checkbox', name=name, value=value, checked=checked):
            text(display)

        self.messageML += doc.getvalue()

    def add_radio_button(self, name, display, value='on', checked='false'):
        """
        This function adds a radio button to a Form Elment.
        Users must specify name, text, and/or optional parameters checked and value.
        Set checked='true' in order to have radio appear selected upon sending.

        Returns a radio button: <radio name="id1" value="on" checked="false">Click Me!</radio>
        """
        doc, tag, text, line = Doc().ttl()
        with tag('radio', name=name, value=value, checked=checked):
            text(display)

        self.messageML += doc.getvalue()

    def add_dropdown_menu(self, dropdown_group):
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
        doc, tag, text, line = Doc().ttl()
        with tag('select', name=dropdown_group[0][0], required=dropdown_group[0][3]):
            for i in dropdown_group:
                with tag('option', value=i[2], selected=i[1]):
                    text(i[4])

        self.messageML += doc.getvalue()

    def add_person_selector(self, name, placeholder='', required='false'):
        """
        This function adds a person selector to the Form Element.
        Users must specify a name and/or optional parameters placeholder and required
        When a user is selected, the corresponding user_id is stored in an
        array corresponding to the name parameter

        Returns a Person Selector:  <person-selector name="awesome-users" placeholder="enter names..." required="false" />
        """
        doc, tag, text, line = Doc().ttl()
        doc.stag('person-selector', name=name, placeholder=placeholder, required=required)

        self.messageML += doc.getvalue()

    def add_table_selector(self, position, type, type_name, header_list, body_list, footer_list):
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
        doc, tag, text, line = Doc().ttl()
        with tag('table'):
            with tag('thead'):
                with tag('tr'):
                    if position == 'left':
                        if type == 'button':
                            line('td', 'Select')
                            for i in table_selector:
                                for j in header_list:
                                    line('td', j)
                        else:
                            with tag('td'):
                                doc.input(name='table-header', type='checkbox')
                                for j in header_list:
                                    line('td', j)
                    else:
                        if type == 'button':
                            for j in header_list:
                                line('td', j)
                            line('td', 'Select')

                        else:
                            for i in table_selector:
                                for j in header_list:
                                    line('td', j)
                            with tag('td'):
                                doc.input(name='table-header', type='checkbox')

            with tag('tbody'):
                for num, j in enumerate(body_list, start=1):
                    with tag('tr'):
                        if position == 'left':
                            with tag('td'):
                                if type == 'button':
                                    with tag('button', name=type_name + str(num)):
                                        text('Button')
                                else:
                                    doc.input(name=type_name + str(num), type='checkbox')
                            for k in j:
                                line('td', k)
                        else:
                            for k in j:
                                line('td', k)
                            with tag('td'):
                                if type == 'button':
                                    with tag('button', name=type_name + str(num)):
                                        text('Button')
                                else:
                                    doc.input(name=type_name + str(num), type='checkbox')

            with tag('tfoot'):
                with tag('tr'):
                    if position == 'left':
                        with tag('td'):
                            if type == 'button':
                                with tag('button', name="footer"):
                                    text('Button')
                            else:
                                doc.input(name='table-footer', type='checkbox')
                        for j in footer_list:
                            line('td', j)
                    else:
                        for j in footer_list:
                            line('td', j)
                        with tag('td'):
                            if type == 'button':
                                with tag('button', name="footer"):
                                    text('Button')
                            else:
                                doc.input(name='table-footer', type='checkbox')

        self.messageML += doc.getvalue()
