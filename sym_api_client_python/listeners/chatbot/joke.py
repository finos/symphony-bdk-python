import requests
import logging
import json
from time import sleep


class JokeClient:

    def __init__(self, bot_client):
        self.bot_client = bot_client

    def get_random_joke(self):
        logging.debug('Getting a random joke..')
        url = 'https://official-joke-api.appspot.com/jokes/random'

        try:
            response = requests.get(url)
            response_body = json.loads(response.text)
            setup = response_body['setup']
            punchline = response_body['punchline']
            return setup, punchline
        except requests.exception.HTTPError as e:
            return "", ""

    def send_joke(self, stream_id):
        setup, punchline = self.get_random_joke()
        for line in setup, punchline:
            msg_to_send = dict(
                message='<messageML><div class="wysiwyg">' +
                        '<p>' +
                        line +
                        '</p></div>'
                        '</messageML>')
            self.bot_client.get_message_client(). \
                send_msg(stream_id, msg_to_send)
            sleep(3)
        self.bot_client.get_message_client().send_msg_with_attachment(
            stream_id,
            '<messageML>A png to make you happy</messageML>',
            'gif.png',
            './sym_api_client_python/listeners/chatbot/giphy.png')
