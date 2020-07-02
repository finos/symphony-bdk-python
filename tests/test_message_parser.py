import logging
import unittest

from sym_api_client_python.processors.sym_message_parser import SymMessageParser


class TestMessageParser(unittest.TestCase):

    def setUp(self):
        logging.debug('testing Message Parser File:')
        self.message_parser = SymMessageParser()
        self.test_message_json = {
                            "messageId": "LKX55AtesGPxrv16ed_TIX___pMru4hmbQ",
                            "timestamp": 1566929352601,
                            "message": "<div data-format=\"PresentationML\" data-version=\"2.0\" class=\"wysiwyg\"><p><span class=\"entity\" data-entity-id=\"0\">$aapl</span> <span class=\"entity\" data-entity-id=\"1\">$amzn</span> <span class=\"entity\" data-entity-id=\"2\">$nasdaq</span></p></div>",
                            "data": "{\"0\":{\"id\":[{\"type\":\"org.symphonyoss.fin.security.id.ticker\",\"value\":\"aapl\"}],\"type\":\"org.symphonyoss.fin.security\",\"version\":\"1.0\"},\"1\":{\"id\":[{\"type\":\"org.symphonyoss.fin.security.id.ticker\",\"value\":\"amzn\"}],\"type\":\"org.symphonyoss.fin.security\",\"version\":\"1.0\"},\"2\":{\"id\":[{\"type\":\"org.symphonyoss.fin.security.id.ticker\",\"value\":\"nasdaq\"}],\"type\":\"org.symphonyoss.fin.security\",\"version\":\"1.0\"}}",
                            "user": {
                                "userId": 349026222344902,
                                "firstName": "Reed",
                                "lastName": "Feldman",
                                "displayName": "Reed Feldman (Develop 2)",
                                "email": "reed.feldman@symphony.com",
                                "username": "reed.feldman@symphony.com"
                            },
                            "stream": {
                                "streamId": "sOKpwRk_5_N838P10ATuFX___pNk9zJndA",
                                "streamType": "ROOM"
                            },
                            "externalRecipients": "false",
                            "userAgent": "DESKTOP-40.0.0-10665-MacOSX-10.14.6-Chrome-76.0.3809.100",
                            "originalFormat": "com.symphony.messageml.v2"
                        }

    def test_get_text(self):
        print(self.message_parser.get_text(self.test_message_json))

    def test_get_im_firstname(self):
        print(self.message_parser.get_im_first_name(self.test_message_json))

    def test_get_stream_id(self):
        print(self.message_parser.get_stream_id(self.test_message_json))

    def test_get_mentions(self):
        print(self.message_parser.get_mentions(self.test_message_json))

    def test_get_mention_ids(self):
        print(self.message_parser.get_mention_ids(self.test_message_json))

    def test_get_hash_tags(self):
        print(self.message_parser.get_hash_tags(self.test_message_json))

    def test_get_hash_tag_values(self):
        print(self.message_parser.get_hash_tag_values(self.test_message_json))

    def test_cash_tags(self):
        print(self.message_parser.get_cash_tags(self.test_message_json))

    def test_get_cash_tag_values(self):
        print(self.message_parser.get_cash_tag_values(self.test_message_json))


if __name__ == '__main__':
    unittest.main()
