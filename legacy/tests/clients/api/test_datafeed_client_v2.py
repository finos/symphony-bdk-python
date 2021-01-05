import json
import os
import unittest
from unittest.mock import patch

from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.configure.configure import SymConfig


@patch('sym_api_client_python.clients.sym_bot_client.requests.sessions.Session.request')
class TestDataFeedClientV2(unittest.TestCase):
    def setUp(self):
        configure = SymConfig(get_path_relative_to_resources_folder('./bot-config.json'))
        configure.load_config()
        configure.data['datafeedVersion'] = 'v2'

        bot_client = SymBotClient(SymBotRSAAuth(configure), configure)

        self.datafeed_client = bot_client.get_datafeed_client()

    def test_create_datafeed(self, mock_request):
        mock_response, url_call = mocked_response('CREATE_DATAFEED', self.datafeed_client.config.data['agentUrl'])
        mock_request.return_value = mock_response
        datafeed_id = self.datafeed_client.create_datafeed()

        self.assertEqual(mock_response.status_code, 201)
        self.assertEqual(datafeed_id, '21449143d35a86461e254d28697214b4_f')
        mock_request.assert_called_with('POST', url_call)

    def test_list_datafeed(self, mock_request):
        mock_response, url_call = mocked_response('LIST_DATAFEED', self.datafeed_client.config.data['agentUrl'])
        mock_request.return_value = mock_response
        datafeed_ids = self.datafeed_client.list_datafeed_id()

        self.assertEqual(mock_response.status_code, 200)
        self.assertEqual(datafeed_ids[0]['id'], mock_response.get_json()[0]['id'])
        self.assertEqual(datafeed_ids[1]['id'], mock_response.get_json()[1]['id'])
        self.assertEqual(datafeed_ids[2]['id'], mock_response.get_json()[2]['id'])
        mock_request.assert_called_with('GET', url_call)

    def test_read_datafeed_empty_ackid(self, mock_request):
        """Test Datafeed Read first call conversation

        Test of handling of ackId when not provided to read_datafeed and call of the function with the right parameters"""
        mock_response, url_call = mocked_response('READ_DATAFEED', self.datafeed_client.config.data['agentUrl'],
                                                  'test_datafeed_id')
        mock_request.return_value = mock_response
        events = self.datafeed_client.read_datafeed('test_datafeed_id')
        ack_id = self.datafeed_client.datafeed_client.get_ack_id()

        self.assertEqual(mock_response.status_code, 200)
        self.assertEqual(ack_id, mock_response.get_json()['ackId'])
        self.assertEqual(events, mock_response.get_json()['events'])
        mock_request.assert_called_with('POST', url_call, json={'ackId': ''})

    def test_read_datafeed(self, mock_request):
        """Test a datafeed read during conversation

        Testing the handling of the ackId when provided to read_datafeed() and call of the function with the right parameters """
        mock_response, url_call = mocked_response('READ_DATAFEED', self.datafeed_client.config.data['agentUrl'],
                                                  'test_datafeed_id')
        mock_request.return_value = mock_response
        events = self.datafeed_client.read_datafeed('test_datafeed_id', 'test_ack_id')
        ack_id = self.datafeed_client.datafeed_client.get_ack_id()

        self.assertEqual(mock_response.status_code, 200)
        self.assertEqual(ack_id, mock_response.get_json()['ackId'])
        self.assertEqual(events, mock_response.get_json()['events'])
        mock_request.assert_called_with('POST', url_call, json={'ackId': 'test_ack_id'})

    def test_delete_datafeed(self, mock_request):
        """Test deleting the datafeed

        Because it's a no content response, we need to make sure of the call parameters """
        mock_response, url_call = mocked_response('DELETE_DATAFEED', self.datafeed_client.config.data['agentUrl'],
                                                  'test_datafeed_id')
        mock_request.return_value = mock_response
        self.datafeed_client.delete_datafeed('test_datafeed_id')

        self.assertEqual(mock_response.status_code, 204)
        mock_request.assert_called_with('DELETE', url_call)


def get_path_relative_to_resources_folder(path_relative_to_resources):
    path_to_resources = os.path.join(os.path.dirname(__file__), '../../resources/', path_relative_to_resources)
    return os.path.normpath(path_to_resources)


def url_method_builder(base_url, url):
    return base_url + url


# This method will be used by the mock to replace Session.request
def mocked_response(agent_call, agent_host, *datafeed_id):
    if agent_call == 'CREATE_DATAFEED':
        return MockResponse(201, get_path_relative_to_resources_folder('./response_content/datafeed_v2/create_datafeed_v2.json')), \
               url_method_builder(agent_host, '/agent/v5/datafeeds')
    elif agent_call == 'LIST_DATAFEED':
        return MockResponse(200, get_path_relative_to_resources_folder('./response_content/datafeed_v2/list_datafeed_v2.json')), \
               url_method_builder(agent_host, '/agent/v5/datafeeds')
    elif agent_call == 'READ_DATAFEED':
        if len(datafeed_id) == 0:
            raise ValueError('If datafeed id is provided, it should not be empty')
        else:
            return MockResponse(200, get_path_relative_to_resources_folder('./response_content/datafeed_v2/read_datafeed_v2.json')), \
                   url_method_builder(agent_host, '/agent/v5/datafeeds/{0}/read'.format(datafeed_id[0]))
    elif agent_call == 'DELETE_DATAFEED':
        if len(datafeed_id) == 0:
            raise ValueError('If datafeed id is provided, it should not be empty')
        else:
            return MockResponse(204, ''), url_method_builder(agent_host,
                                                             '/agent/v5/datafeeds/{0}'.format(datafeed_id[0]))
    else:
        return MockResponse(None, 404)


class MockResponse:
    def __init__(self, status_code, path):
        self.status_code = status_code
        if len(path) == 0:
            self.data = ''
        else:
            with open(os.path.realpath(path)) as json_file:
                self.data = json.load(json_file)
        self.text = json.dumps(self.data)

    def get_json(self):
        return self.data

    def get_text(self):
        return json.dumps(self.data)
