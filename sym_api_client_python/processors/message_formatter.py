from yattag import Doc

class MessageFormatter:

    def __init__(self):
        pass

    def format_message(self, message):
        """
        appends messageML tags to plain text and returns a dictionary:

        {message : messageML object}
        """
        doc,tag,text,line = Doc().ttl()
        with tag('messageML'):
            text(message)
        return dict(message = doc.getvalue())

    def format_element(self, form_object):
        """
        create_messageML() takes in a form object, parses its attritubes/metadata and returns
        a dictionary: {message : messageML object}.  This is the correct format to send
        in the Create Message v4 REST call.

        This messageML object is bootstrapped properly with <form> and
        <messageML> tags so that it can be rendered as an Element as is.
        """

        doc, tag, text, line = Doc().ttl()
        with tag('messageML'):
            with tag('form', id = form_object.form_id):
                with tag(form_object.headers[0][0]):
                    text(form_object.headers[0][1])
                for i, j, k in form_object.buttons:
                    with tag('button', name=i, type=j):
                        text(k)
                for i,j,k,l,m,n in form_object.text_fields:
                    with tag('text-field', name=i, placeholder=j, required=k, maxlength=l, minlength=m):
                        text(n)
                for i,j,k,l,m,n,o in form_object.masked_text_fields:
                    with tag('text-field', name=i, placeholder=j, required=k, masked=l, maxlength=m, minlength=n):
                        text(o)
                for i,j,k,l in form_object.text_areas:
                    with tag('textarea', name=i, placeholder=j, required=k):
                        text(l)
                for i,j,k,l in form_object.check_boxes:
                    with tag('checkbox', name=i, value=j, checked=k):
                        text(l)
                for i,j,k,l in form_object.radio_buttons:
                    with tag('radio', name=i, value=j, checked=k):
                        text(l)
                for i in form_object.dropdown_menu_groups:
                    with tag('select', name=i[0][0], required=i[0][3]):
                        for j in i:
                            with tag('option', value=j[2], selected=j[1]):
                                text(j[4])
                for i, j, k in form_object.person_selectors:
                    doc.stag('person-selector', name=i, placeholder=j, required=k)

                with tag('table'):
                    with tag('thead'):
                        with tag('tr'):
                            if form_object.table_selectors[0][0] == 'left':
                                if form_object.table_selectors[0][1] == 'button':
                                    print('left and button')
                                    line('td', 'Select')
                                    for i in form_object.table_selectors:
                                        for j in i[3]:
                                            line('td', j)
                                else:
                                    print('left and checkbox')
                                    with tag('td'):
                                        doc.input(name = 'table-header', type = 'checkbox')
                                    for i in form_object.table_selectors:
                                        for j in i[3]:
                                            line('td', j)
                            else:
                                if form_object.table_selectors[0][1] == 'button':
                                    print('right and button')
                                    for i in form_object.table_selectors:
                                        for j in i[3]:
                                            line('td', j)
                                    line('td', 'Select')

                                else:
                                    print('right and checkbox')
                                    for i in form_object.table_selectors:
                                        for j in i[3]:
                                            line('td', j)
                                    with tag('td'):
                                        doc.input(name = 'table-header', type = 'checkbox')

                    with tag('tbody'):
                            for i in form_object.table_selectors:
                                    for num, j in enumerate(i[4], start=1):
                                        with tag('tr'):
                                            if form_object.table_selectors[0][0] == 'left':
                                                with tag('td'):
                                                    if form_object.table_selectors[0][1] == 'button':
                                                        with tag('button', name=i[2]+str(num)):
                                                            text('Button')
                                                    else:
                                                        doc.input(name=i[2]+str(num), type='checkbox')
                                                for k in j:
                                                    line('td', k)
                                            else:
                                                for k in j:
                                                    line('td', k)
                                                with tag('td'):
                                                    if form_object.table_selectors[0][1] == 'button':
                                                        with tag('button', name=i[2]+str(num)):
                                                            text('Button')
                                                    else:
                                                        doc.input(name=i[2]+str(num), type='checkbox')

                    with tag('tfoot'):
                            for i in form_object.table_selectors:
                                with tag('tr'):
                                    if form_object.table_selectors[0][0] == 'left':
                                        with tag('td'):
                                            if form_object.table_selectors[0][1] == 'button':
                                                with tag('button', name="footer"):
                                                    text('Button')
                                            else:
                                                doc.input(name='table-footer', type='checkbox')
                                        for j in i[5]:
                                            line('td', j)
                                    else:
                                        for j in i[5]:
                                            line('td', j)
                                        with tag('td'):
                                            if form_object.table_selectors[0][1] == 'button':
                                                with tag('button', name="footer"):
                                                    text('Button')
                                            else:
                                                doc.input(name='table-footer', type='checkbox')


        return dict(message = doc.getvalue())
