from yattag import Doc


class MessageFormatter:

    def __init__(self):
        pass

    def format_message(self, message):
        """
        appends messageML tags to plain text and returns a dictionary:

        {message : messageML object}
        """
        doc, tag, text, line = Doc().ttl()
        with tag('messageML'):
            text(message)

        return dict(message=doc.getvalue())
