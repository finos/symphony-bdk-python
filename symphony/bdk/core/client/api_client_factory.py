"""Module containing the ApiClientFactory class.
"""
import logging
import sys
from importlib.metadata import distribution, PackageNotFoundError
from ssl import SSLError

import urllib3
from aiohttp.hdrs import USER_AGENT

from symphony.bdk.core.client.trace_id import add_x_trace_id, X_TRACE_ID
from symphony.bdk.gen.api_client import ApiClient
from symphony.bdk.gen.configuration import Configuration

KEY_AUTH = "/keyauth"
SESSION_AUTH = "/sessionauth"
AGENT = "/agent"
RELAY = "/relay"
POD = "/pod"
LOGIN = "/login"

logger = logging.getLogger(__name__)


class ApiClientFactory:
    """Factory responsible for creating ApiClient instances for each main Symphony's components.
    """

    def __init__(self, config):
        self._config = config
        self._login_client = self._get_api_client(self._config.pod, LOGIN)
        self._pod_client = self._get_api_client(self._config.pod, POD)
        self._relay_client = self._get_api_client(self._config.key_manager, RELAY)
        self._agent_client = self._get_api_client(self._config.agent, AGENT)
        self._session_auth_client = self._get_api_client_with_client_cert(self._config.session_auth, SESSION_AUTH,
                                                                          self._config.bot.certificate.path)
        self._key_auth_client = self._get_api_client_with_client_cert(self._config.key_manager, KEY_AUTH,
                                                                      self._config.bot.certificate.path)
        self._app_session_auth_client = self._get_api_client_with_client_cert(self._config.session_auth, SESSION_AUTH,
                                                                              self._config.app.certificate.path)

    def get_login_client(self) -> ApiClient:
        """Returns a fully initialized ApiClient for Login API.

        :return: an ApiClient instance for Login API.
        """
        return self._login_client

    def get_pod_client(self) -> ApiClient:
        """Returns a fully initialized ApiClient for Pod API.

        :return: an ApiClient instance for Pod API.
        """
        return self._pod_client

    def get_relay_client(self) -> ApiClient:
        """Returns a fully initialized ApiClient for Key Manager API.

        :return: an ApiClient instance for Key Manager API.
        """
        return self._relay_client

    def get_session_auth_client(self) -> ApiClient:
        """Returns a fully initialized ApiClient for Session Auth Api for bot certificate authentication.

        :return: an ApiClient instance for Session Auth Api for bot certificate authentication.
        """
        return self._session_auth_client

    def get_key_auth_client(self) -> ApiClient:
        """Returns a fully initialized ApiClient for Key Auth Api for bot certificate authentication.

        :return: an ApiClient instance for Key Auth Api for bot certificate authentication.
        """
        return self._key_auth_client

    def get_app_session_auth_client(self) -> ApiClient:
        """Returns a fully initialized ApiClient for Session Auth API for certificate OBO authentication.

        :return: an ApiClient instance for Session Auth API.
        """
        return self._app_session_auth_client

    def get_agent_client(self) -> ApiClient:
        """Returns a fully initialized ApiClient for Agent API.

        :return: an ApiClient instance for Agent API.
        """
        return self._agent_client

    async def close_clients(self):
        """
        Close all the existing api clients created by the api client factory.
        """
        await self._login_client.close()
        await self._relay_client.close()
        await self._pod_client.close()
        await self._agent_client.close()
        await self._session_auth_client.close()
        await self._key_auth_client.close()
        await self._app_session_auth_client.close()

    def _get_api_client(self, server_config, context) -> ApiClient:
        configuration = self._get_client_config(context, server_config)
        return ApiClientFactory._get_api_client_from_config(configuration, server_config)

    def _get_api_client_with_client_cert(self, server_config, context, certificate_path) -> ApiClient:
        configuration = self._get_client_config(context, server_config)
        configuration.cert_file = certificate_path

        return ApiClientFactory._get_api_client_from_config(configuration, server_config)

    def _get_client_config(self, context, server_config):
        configuration = Configuration(host=(server_config.get_base_path() + context), discard_unknown_keys=True)
        configuration.verify_ssl = True
        configuration.ssl_ca_cert = self._config.ssl.trust_store_path
        if server_config.proxy is not None:
            ApiClientFactory._configure_proxy(server_config, configuration)
        return configuration

    @staticmethod
    def _get_api_client_from_config(client_config, server_config):
        try:
            client = ApiClient(configuration=client_config)
            ApiClientFactory._add_headers(client, server_config)
            return client
        except SSLError as exc:
            logger.exception("SSL error when instantiating clients, please check certificates are valid")
            raise exc

    @staticmethod
    def _add_headers(client, server_config):
        default_headers = ApiClientFactory._sanitized_default_headers(server_config)

        for header_name, header_value in default_headers.items():
            client.set_default_header(header_name, header_value)
        client.user_agent = ApiClientFactory._user_agent(server_config)

        if X_TRACE_ID.lower() not in (header_name.lower() for header_name in default_headers.keys()):
            client._ApiClient__call_api = add_x_trace_id(client._ApiClient__call_api)

    @staticmethod
    def _configure_proxy(server_config, configuration):
        proxy_config = server_config.proxy
        user_agent = ApiClientFactory._user_agent(server_config)

        configuration.proxy = proxy_config.get_url()
        if proxy_config.are_credentials_defined():
            configuration.proxy_headers = urllib3.util.make_headers(proxy_basic_auth=proxy_config.get_credentials(),
                                                                    user_agent=user_agent)
        else:
            configuration.proxy_headers = urllib3.util.make_headers(user_agent=user_agent)

    @staticmethod
    def _sanitized_default_headers(server_config):
        default_headers = server_config.default_headers if server_config.default_headers is not None else {}

        # we do this because we want to handle user-agent header separately
        # for client configuration and proxy header
        return {header_key: default_headers[header_key] for header_key in default_headers
                if header_key.lower() != USER_AGENT.lower()}

    @staticmethod
    def _user_agent(server_config):
        default_headers = server_config.default_headers if server_config.default_headers is not None else {}

        for header_key, header_value in default_headers.items():
            if header_key.lower() == USER_AGENT.lower():
                return header_value

        return ApiClientFactory._default_user_agent()

    @staticmethod
    def _default_user_agent():
        return f"Symphony-BDK-Python/{ApiClientFactory._bdk_version()} Python/{ApiClientFactory._python_version()}"

    @staticmethod
    def _bdk_version():
        try:
            return distribution("sym_api_client_python").version
        except PackageNotFoundError:
            # the above won't work when bdk is not installed as a pypi package,
            # e.g. for scripts in the examples folder
            return "2.0"

    @staticmethod
    def _python_version():
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
