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

    def format_element(self, form_object_ML):
        """
        create_messageML() takes in a form object, parses its attritubes/metadata and returns
        a dictionary: {message : messageML object}.  This is the correct format to send
        in the Create Message v4 REST call.

        This messageML object is bootstrapped properly with <form> and
        <messageML> tags so that it can be rendered as an Element as is.
        """

        doc, tag, text, line = Doc().ttl()
        with tag('messageML'):
            tag('form', id = form_object.form_id)




        return dict(message = '<messageML>' + messageML_string + '</messageML>')
