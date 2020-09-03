import json

from bs4 import BeautifulSoup


class SymMessageParser:
    """
    MessageParser class takes message_data as its only parameter.
    message action data is a json object passed from DataFeedEventService
    to the RoomListenerImplementation or IMListenerImplementation class.
    The message_data json object follows the structure below:

    "messageId": "KcIMpk9tHtY8zMmkyGyCK3___pNqVF2QbQ",
    "timestamp": 1565879149167,
    "message": "<div data-format=\"PresentationML\" data-version=\"2.0\" class=\"wysiwyg\"><p><span class=\"entity\" data-entity-id=\"0\">@reed-bot-demo</span> </p></div>",
    "data": "{\"0\":{\"id\":[{\"type\":\"com.symphony.user.userId\",\"value\":\"344147139497165\"}],\"type\":\"com.symphony.user.mention\"}}",
    "user": {
        "userId": 344147139494862,
        "firstName": "Reed",
        "lastName": "Feldman",
        "displayName": "Reed Feldman (SUP)",
        "email": "reed.feldman@symphony.com",
        "username": "reedUAT"
    },
    "stream": {
        "streamId": "pDWC8aUE7IYlK8b9lChaM3___pNuPcIWdA",
        "streamType": "ROOM"
    },
    "externalRecipients": false,
    "userAgent": "DESKTOP-40.0.0-10600-MacOSX-10.14.6-Chrome-76.0.3809.100",
    "originalFormat": "com.symphony.messageml.v2"
}

    This class provides methods to the developer to easily access data in this
    message_data payload for quick bot development.
    """

    def __init__(self):
        self.HASHTAG_TYPE = "org.symphonyoss.taxonomy.hashtag"
        self.CASHTAG_TYPE = "org.symphonyoss.fin.security.id.ticker"
        self.MENTION_TYPE = "com.symphony.user.userId"

    def get_text(self, message_data):
        text_arr = []
        msg_xml = message_data['message']
        soup = BeautifulSoup(msg_xml, 'html.parser')
        for i in soup.find_all('div'):
            text_arr.extend(i.text.split(' '))
        return text_arr

    def get_im_first_name(self, message_data):
        return message_data['user']['firstName']

    def get_im_last_name(self, message_data):
        return message_data['user']['lastName']

    def get_im_name(self, message_data):
        return str(message_data['user']['firstName']) + ' ' + str(message_data['user']['lastName'])

    def get_stream_id(self, message_data):
        return message_data['stream']['streamId']

    def __get_tags(self, json_nodes, tag_type):
        tags = []
        if json_nodes:
            for k, v in json_nodes.items():
                if 'id' in v and len(v['id']) > 0 and 'type' in v['id'][0] and v['id'][0]['type'] == tag_type and 'value' in v['id'][0]:
                    tags.append(v['id'][0]['value'])
        return tags

    def get_mentions(self, message_data):
        mention_arr = []
        msg_xml = message_data['message']
        soup = BeautifulSoup(msg_xml, 'html.parser')
        for i in soup.find_all('span'):
            mention_arr.append(i.text)
        return mention_arr

    def get_mention_ids(self, message_data):
        d = json.loads(message_data['data'])
        return self.__get_tags(d, self.MENTION_TYPE)

    def get_hash_tags(self, message_data):
        tag_arr = []
        msg_xml = message_data['message']
        soup = BeautifulSoup(msg_xml, 'html.parser')
        for i in soup.find_all('span'):
            tag_arr.append(i.text)
        return tag_arr

    def get_hash_tag_values(self, message_data):
        d = json.loads(message_data['data'])
        return self.__get_tags(d, self.HASHTAG_TYPE)

    def get_cash_tags(self, message_data):
        cash_arr = []
        msg_xml = message_data['message']
        soup = BeautifulSoup(msg_xml, 'html.parser')
        for i in soup.find_all('span'):
            cash_arr.append(i.text)
        return cash_arr

    def get_cash_tag_values(self, message_data):
        d = json.loads(message_data['data'])
        return self.__get_tags(d, self.CASHTAG_TYPE)

