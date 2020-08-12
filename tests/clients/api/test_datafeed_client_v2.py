import pytest
from unittest.mock import patch
import json
import os

from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.configure.configure import SymConfig


@pytest.fixture
def datafeed_client():
    configure = SymConfig('./tests/resources/bot-config.json', __file__)
    configure.load_config()
    configure.data["datafeedVersion"] = "v2"

    # auth = SymBotRSAAuth(configure)
    auth = SymBotRSAAuth(configure)
    auth.session_token = "eyJhbGciOiJSUzUxMiJ9.eyJzdWIiOiJ0ZXN0LWJvdCIsImlzcyI6InN5bXBob255Iiwic2Vzc2lvbklkIjoiZmRiOTAxMmQzOTgwMGE3NzNkMTJjYWFmZGY5MjU4ZjZjOWEyMTE2MmYyZDU1ODQ3M2Y5ZDU5MDUyNjA0Mjg1ZjU0MWM5Yzg0Mzc5YTE0MjZmODNiZmZkZTljYmQ5NjRjMDAwMDAxNmRmMjMyODIwNTAwMDEzZmYwMDAwMDAxZTgiLCJ1c2VySWQiOiIzNTE3NzUwMDE0MTIwNzIifQ.DlQ_-sAqZLlAcVTr7t_PaYt_Muq_P82yYrtbEEZWMpHMl-7qCciwfi3uXns7oRbc1uvOrhQd603VKQJzQxaZBZBVlUPS-2ysH0tBpCS57ocTS6ZwtQwPLCZYdT-EZ70EzQ95kG6P5TrLENH6UveohgeDdmyzSPOEiwyEUjjmzaXFE8Tu0R3xQDwl-BKbsyUAAgd1X7T0cUDC3WIDl9xaTvyxavep4ZJnZJl4qPc1Tan0yU7JrxtXeD8uwNYlKLudT3UVxduFPMQP_2jyj5Laa-YWGKvRtXkcy2d3hzf4ll1l1wVnyJc1e6hW2EnRlff_Nxge-QCJMcZ_ALrpOUtAyQ"

    # Initialize SymBotClient with auth and configure objects
    bot_client = SymBotClient(auth, configure)

    # Initialize datafeed service
    datafeed_client = bot_client.get_datafeed_client()
    return datafeed_client


def test_create_datafeed(datafeed_client):
    with patch('sym_api_client_python.clients.sym_bot_client.requests.sessions.Session.request') as mock_request:
        mock_response, url_call = mocked_response('CREATE_DATAFEED', datafeed_client.config.data["agentHost"])
        mock_request.return_value = mock_response
        datafeed_id = datafeed_client.create_datafeed()

    assert mock_response.status_code == 201
    assert datafeed_id == "21449143d35a86461e254d28697214b4_f"

    mock_request.assert_called_with("POST", url_call)


def test_list_datafeed(datafeed_client):
    with patch('sym_api_client_python.clients.sym_bot_client.requests.sessions.Session.request') as mock_request:
        mock_response, url_call = mocked_response('LIST_DATAFEED', datafeed_client.config.data["agentHost"])
        mock_request.return_value = mock_response
        datafeed_ids = datafeed_client.list_datafeed_id()

    assert mock_response.status_code == 200
    assert datafeed_ids[0]["id"] == mock_response.get_json()[0]["id"]
    assert datafeed_ids[1]["id"] == mock_response.get_json()[1]["id"]
    assert datafeed_ids[2]["id"] == mock_response.get_json()[2]["id"]
    mock_request.assert_called_with("GET", url_call)

def test_read_datafeed_empty_ackid(datafeed_client):
    """Test Datafeed Read first call conversation

    Test of handling of ackId when not provided to read_datafeed and call of the function with the right parameters"""
    with patch('sym_api_client_python.clients.sym_bot_client.requests.sessions.Session.request') as mock_request:
        mock_response, url_call = mocked_response('READ_DATAFEED', datafeed_client.config.data["agentHost"], "test_datafeed_id")
        mock_request.return_value = mock_response
        events = datafeed_client.read_datafeed("test_datafeed_id")
        ack_id = datafeed_client.datafeed_client.get_ack_id()

    assert mock_response.status_code == 200
    assert ack_id == mock_response.get_json()["ackId"]
    assert events == mock_response.get_json()["events"]
    mock_request.assert_called_with("POST", url_call, json={'ackId': ''})

def test_read_datafeed(datafeed_client):
    """Test a datafeed read during conversation

    Testing the handling of the ackId when provided to read_datafeed() and call of the function with the right parameters """
    with patch('sym_api_client_python.clients.sym_bot_client.requests.sessions.Session.request') as mock_request:
        mock_response, url_call = mocked_response('READ_DATAFEED', datafeed_client.config.data["agentHost"], "test_datafeed_id")
        mock_request.return_value = mock_response
        events = datafeed_client.read_datafeed("test_datafeed_id", "test_ack_id")
        ack_id = datafeed_client.datafeed_client.get_ack_id()

    assert mock_response.status_code == 200
    assert ack_id == mock_response.get_json()["ackId"]
    assert events == mock_response.get_json()["events"]
    mock_request.assert_called_with("POST", url_call, json={'ackId': 'test_ack_id'})

def test_delete_datafeed(datafeed_client):
    """Test deleting the datafeed

    Because it's a no content response, we need to make sure of the call parameters """
    with patch('sym_api_client_python.clients.sym_bot_client.requests.sessions.Session.request') as mock_request:
        mock_response, url_call = mocked_response('DELETE_DATAFEED', datafeed_client.config.data["agentHost"], "test_datafeed_id")
        mock_request.return_value = mock_response
        datafeed_client.delete_datafeed("test_datafeed_id")

    assert mock_response.status_code == 204 # no content
    mock_request.assert_called_with("DELETE", url_call)

def url_method_builder(base_url, url):
    return base_url + url

# This method will be used by the mock to replace Session.request
def mocked_response(agent_call, agent_host, *datafeed_id):
    if agent_call == 'CREATE_DATAFEED':
        return MockResponse(201, "./tests/resources/response_content/datafeed_v2/create_datafeed_v2.json"), url_method_builder(agent_host, '/agent/v5/datafeeds')
    elif agent_call == 'LIST_DATAFEED':
        return MockResponse(200, "./tests/resources/response_content/datafeed_v2/list_datafeed_v2.json"), url_method_builder(agent_host, '/agent/v5/datafeeds')
    elif agent_call == 'READ_DATAFEED':
        if len(datafeed_id) == 0:
            raise ValueError("If datafeed id is provided, it should not be empty")
        else:
            return MockResponse(200, "./tests/resources/response_content/datafeed_v2/read_datafeed_v2.json"), url_method_builder(agent_host, '/agent/v5/datafeeds/{0}/read'.format(datafeed_id[0]))
    elif agent_call == 'DELETE_DATAFEED':
        if len(datafeed_id) == 0:
            raise ValueError("If datafeed id is provided, it should not be empty")
        else:
            return MockResponse(204, ""), url_method_builder(agent_host, '/agent/v5/datafeeds/{0}'.format(datafeed_id[0]))
    else:
        return MockResponse(None, 404)



class MockResponse:
    def __init__(self, status_code, path):
        self.status_code = status_code
        if len(path) == 0:
            self.data = ""
        else:
            with open(os.path.realpath(path)) as json_file:
                self.data = json.load(json_file)
        self.text = json.dumps(self.data)
    def get_json(self):
        return self.data

    def get_text(self):
        return json.dumps(self.data)

