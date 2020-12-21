import json
import logging
from json.decoder import JSONDecodeError

import aiohttp
import requests
import ssl

from .admin_client import AdminClient
from .api_client import APIClient
from .connections_client import ConnectionsClient
from .datafeed_client import DataFeedClient
from .health_check_client import HealthCheckClient
from .message_client import MessageClient
from .signals_client import SignalsClient
from .stream_client import StreamClient
from .user_client import UserClient
from ..datafeed_event_service import AsyncDataFeedEventService, DataFeedEventService
from ..exceptions.UnauthorizedException import UnauthorizedException

# SymBotClient class is the Client class that has access to all of the other
# client classes upon initialization, SymBotClient class gets an instance of
# each client along with access to all of its methods.
# class contains series of getters for each client
# class also contains config and auth class as a way to pass this info around
# to each client as well class is seen as orchestrator or interface for all
# REST API calls

# Saving this has as a constant because it's easily typoed and used everywhere
_TRUSTSTORE_PATH = "truststorePath"


class SymBotClient(APIClient):

    def __init__(self, auth, config):
        self.auth = auth
        self.config = config
        self.agentConfig = config
        self.datafeed_event_service = None
        self.async_datafeed_event_service = None
        self.datafeed_client = None
        self.msg_client = None
        self.stream_client = None
        self.user_client = None
        self.connections_client = None
        self.signals_client = None
        self.admin_client = None
        self.api_client = None
        self.pod_session = None
        self.async_pod_session = None
        self.agent_session = None
        self.async_agent_session = None
        self.bot_user_info = None
        self.health_check_client = None
        self.async_ssl_context = None


    def get_datafeed_event_service(self, *args, **kwargs):
        if self.datafeed_event_service is None:
            self.datafeed_event_service = DataFeedEventService(self, *args, **kwargs)
        return self.datafeed_event_service

    def get_async_datafeed_event_service(self, *args, **kwargs):
        if self.async_datafeed_event_service is None:
            self.async_datafeed_event_service = AsyncDataFeedEventService(self, *args, **kwargs)
        return self.async_datafeed_event_service

    def get_datafeed_client(self):
        if self.datafeed_client is None:
            self.datafeed_client = DataFeedClient(self)
        return self.datafeed_client

    def get_message_client(self):
        if self.msg_client is None:
            self.msg_client = MessageClient(self)
        return self.msg_client

    def get_admin_client(self):
        if self.admin_client is None:
            self.admin_client = AdminClient(self)
        return self.admin_client

    def get_signals_client(self):
        if self.signals_client is None:
            self.signals_client = SignalsClient(self)
        return self.signals_client

    def get_connections_client(self):
        if self.connections_client is None:
            self.connections_client = ConnectionsClient(self)
        return self.connections_client

    def get_stream_client(self):
        if self.stream_client is None:
            self.stream_client = StreamClient(self)
        return self.stream_client

    def get_user_client(self):
        if self.user_client is None:
            self.user_client = UserClient(self)
        return self.user_client

    def get_api_client(self):
        self.api_client = APIClient(self)

    def get_sym_config(self):
        return self.config

    def get_sym_agent_config(self):
        return self.agentConfig

    def get_sym_auth(self):
        return self.auth

    def get_pod_session(self):
        """This is the method to retrieve the session object for synchronous calls with requests"""
        if self.pod_session is None:
            logging.debug('bot_client/get_pod_session() - creating pod session')
            self.pod_session = requests.Session()
            self.pod_session.headers.update({
                'sessionToken': self.auth.get_session_token(),
                'cache-control': 'no-cache'}
            )
            self.pod_session.proxies.update(self.config.data['podProxyRequestObject'])
            if self.config.data[_TRUSTSTORE_PATH]:
                logging.debug("Setting truststorePath for pod to {}".format(
                    self.config.data[_TRUSTSTORE_PATH]))
                self.pod_session.verify = self.config.data[_TRUSTSTORE_PATH]
        return self.pod_session

    def get_agent_session(self):
        """This is the method to retrieve the session object for synchronous calls with requests"""
        if self.agent_session is None:
            logging.debug('bot_client/get_agent_session() - creating agent session')
            self.agent_session = requests.Session()
            self.agent_session.headers.update({
                'sessionToken': self.auth.get_session_token(),
                'keyManagerToken': self.auth.get_key_manager_token(),
                'cache-control': 'no-cache'}
            )
            self.agent_session.proxies.update(self.config.data['agentProxyRequestObject'])
            if self.config.data[_TRUSTSTORE_PATH]:
                logging.debug("Setting truststorePath for agent to {}".format(
                    self.config.data[_TRUSTSTORE_PATH])
                )
                self.agent_session.verify=self.config.data[_TRUSTSTORE_PATH]

        return self.agent_session

    def execute_rest_call(self, method, path, **kwargs):
        results = None
        session = None
        if path.startswith("/agent/"):
            url = self.config.data["agentUrl"] + path
            session = self.get_agent_session()
        elif path.startswith("/pod/"):
            url = self.config.data["podUrl"] + path
            session = self.get_pod_session()
        else:
            url = path
            session = self.get_agent_session()

        try:
            response = session.request(method, url, **kwargs)
        except requests.exceptions.ConnectionError as err:
            logging.debug(err)
            logging.debug(type(err))
            logging.debug('ensure pod/agent subdomains are correct')
            raise
        if response.status_code == 204:
            results = []
        elif response.status_code == 200 or response.status_code == 201:
            try:
                results = json.loads(response.text)
            except JSONDecodeError:
                results = response.text
        else:
            # Try to get the json to be used to handle the error message
            error_json = None
            text = None
            try:
                error_json = response.json()
            except JSONDecodeError:
                try:
                    text = response.text
                except Exception:
                    text = None
            try:
                super().handle_error(response, self, error_json, text)
            except UnauthorizedException:
                logging.debug('caught UnauthorizedException - try execute_rest_call() again')
                self.execute_rest_call(method, path, **kwargs)
        return results


    def get_async_pod_session(self):
        """This is the method to retrieve the session object for asynchronous calls with aiohttp"""
        if self.async_pod_session is None:
            logging.debug('bot_client/get_pod_session() - creating async pod session')
            self.async_pod_session = aiohttp.ClientSession(
            headers = {
                'sessionToken': self.auth.get_session_token(),
                'cache-control': 'no-cache'}
                )
            # For aiohttp proxies and truststore are handled when the request is made
        return self.async_pod_session

    def get_async_agent_session(self):
        """This is the method to retrieve the session object for asynchronous calls with aiohttp"""
        if self.async_agent_session is None:
            logging.debug('bot_client/get_agent_session() - creating async agent session')
            self.async_agent_session = aiohttp.ClientSession(
            headers = {
                'sessionToken': self.auth.get_session_token(),
                'keyManagerToken': self.auth.get_key_manager_token(),
                'cache-control': 'no-cache'}
            )
            # For aiohttp proxies and truststore are handled when the request is made
        return self.async_agent_session

    # Known issue on this function when using a proxy due to an outstanding issue with aiohttp
    # To workaround this please check README.md
    async def execute_rest_call_async(self, method, path, **kwargs):
        """This is the asynchronous method to hit the rest api, it should be awaited"""
        results = None
        session = None

        if path.startswith("/agent/"):
            url = self.config.data["agentUrl"] + path
            session = self.get_async_agent_session()
            http_proxy = self.config.data['agentProxyRequestObject'].get("http")

        elif path.startswith("/pod/"):
            url = self.config.data["podUrl"] + path
            session = self.get_async_pod_session()
            http_proxy = self.config.data['podProxyRequestObject'].get("http")
        else:
            # TODO: Confirm whether this should just throw
            # Not sure what the best course of action is here, taking pod values
            url = path
            session = self.get_async_pod_session()
            http_proxy = self.config.data['podProxyRequestObject'].get("http")

        # This is to handle the files keyword
        files = kwargs.pop("files", None)

        # The below attempts to handle a files kwarg in the same way that Requests handles it
        if files is not None:
            with aiohttp.MultipartWriter("form-data") as mpwriter:
                for (key, value) in files.items():
                    part = mpwriter.append(value)
                    part.set_content_disposition("form-data", name=key)
            if kwargs.get("data"):
                # This isn't fatal, it's just not yet clear how to handle this in aiohttp
                # This link is the best resource I've seen explaining the issue
                # https://github.com/aio-libs/aiohttp/issues/3571
                raise RuntimeError("Not expecting to find data and files")
            else:
                data = mpwriter
        elif kwargs.get("data") is not None:
            data = kwargs.pop("data")
        else:
            data = None


        try:
            response = await session.request(method, url, proxy=http_proxy, ssl=self.get_async_ssl_context(), data=data, **kwargs)
        except aiohttp.ClientConnectionError as err:
            logging.debug(err)
            logging.debug(type(err))
            logging.debug('ensure pod/agent subdomains are correct')
            raise

        if response.status == 204:
            results = []
        elif response.status == 200:
            text = await response.text()

            try:
                results = json.loads(text)
            except JSONDecodeError:
                results = text
        else:
            # Try to get the json to be used to handle the error message
            error_json = None
            text = None
            try:
                error_json = await response.json()
            except JSONDecodeError:
                try:
                    text = await response.text()
                except Exception:
                    text = None
            try:
                super().handle_error(response, self, error_json, text)
            except UnauthorizedException:
                await self.execute_rest_call_async(method, path, **kwargs)
        return results

    def reauth_client(self):
        self.auth.authenticate()
        if self.pod_session:
            logging.debug('bot_client/reauth_client() - pod session exists')
            self.pod_session.headers.update({
                'sessionToken': self.auth.get_session_token()}
            )
        if self.agent_session:
            logging.debug('bot_client/reauth_client() - agent session exists')
            self.agent_session.headers.update({
                'sessionToken' : self.auth.get_session_token(),
                'keyManagerToken': self.auth.get_key_manager_token()}
            )

        if self.async_pod_session:
            logging.debug('bot_client/reauth_client() - async pod session exists')
            self.async_pod_session = aiohttp.ClientSession(
            headers = {
                'sessionToken': self.auth.get_session_token()}
            )

        if self.async_agent_session:
            logging.debug('bot_client/reauth_client() - async agent session exists')
            self.async_agent_session = aiohttp.ClientSession(
            headers = {
                'sessionToken': self.auth.get_session_token(),
                'keyManagerToken': self.auth.get_key_manager_token()}
            )

    def get_bot_user_info(self):
        if self.bot_user_info is None:
            self.bot_user_info = self.get_user_client().get_session_user()
        return self.bot_user_info

    def get_health_check_client(self):
        if self.health_check_client is None:
            self.health_check_client = HealthCheckClient(self)
        return self.health_check_client

    #Required for aiohttp to use truststore
    def get_async_ssl_context(self):
        if self.async_ssl_context is None:
            if self.config.data[_TRUSTSTORE_PATH]:
                logging.debug("Setting truststorePath for async calls to {}".format(self.config.data[_TRUSTSTORE_PATH]))
                self.async_ssl_context = ssl.create_default_context(cafile=self.config.data[_TRUSTSTORE_PATH])
            else:
                self.async_ssl_context = ssl.create_default_context()
        return self.async_ssl_context

    async def close_async_sessions(self):
        """Close the open aiohttp.ClientSession objects

        In general this shouldn't be necessary as the interpreter should tear down
        any Python objects, and subsequently the OS should terminate any other
        resources (in this case sockets). However due to bugs in the Python standard
        library certain situations trigger a race condition between asyncio and the
        logging library that clobbers the stacktrace and raises a NameError. This
        just ensures that doesn't happen and gives a cleaner output from the SDK.

        For most usecases this method can be safely omitted.
        """
        logging.debug("Manually closing sessions")
        if self.async_pod_session:
            await self.async_pod_session.close()
            self.async_pod_session = None

        if self.async_agent_session:
            await self.async_agent_session.close()
            self.async_agent_session = None
