"""Module containing the ApiClientFactory class.
"""
import sys
from importlib.metadata import distribution, PackageNotFoundError

import urllib3
from aiohttp.hdrs import USER_AGENT

from symphony.bdk.core.client.trace_id import add_x_trace_id
from symphony.bdk.gen.api_client import ApiClient
from symphony.bdk.gen.configuration import Configuration


class ApiClientFactory:
    """Factory responsible for creating ApiClient instances for each main Symphony's components.
    """

    def __init__(self, config):
        self._config = config
        self._login_client = self._get_api_client(self._config.pod, "/login")
        self._pod_client = self._get_api_client(self._config.pod, "/pod")
        self._relay_client = self._get_api_client(self._config.key_manager, "/relay")
        self._agent_client = self._get_api_client(self._config.agent, "/agent")
        self._session_auth_client = self._get_api_client(self._config.session_auth, "/sessionauth")

    def get_login_client(self) -> ApiClient:
        """Returns a fully initialized ApiClient for Login API.

        :return: a ApiClient instance for Login API.
        """
        return self._login_client

    def get_pod_client(self) -> ApiClient:
        """Returns a fully initialized ApiClient for Pod API.

        :return: a ApiClient instance for Pod API.
        """
        return self._pod_client

    def get_relay_client(self) -> ApiClient:
        """Returns a fully initialized ApiClient for Key Manager API.

        :return: a ApiClient instance for Key Manager API.
        """
        return self._relay_client

    def get_session_auth_client(self) -> ApiClient:
        """Returns a fully initialized ApiClient for Session Auth API.

        :return: a ApiClient instance for Session Auth API.
        """
        return self._session_auth_client

    def get_agent_client(self) -> ApiClient:
        """Returns a fully initialized ApiClient for Agent API.

        :return: a ApiClient instance for Agent API.
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

    def _get_api_client(self, server_config, context) -> ApiClient:
        configuration = Configuration(host=(server_config.get_base_path() + context))
        configuration.verify_ssl = True
        configuration.ssl_ca_cert = self._config.ssl.trust_store_path

        if server_config.proxy is not None:
            ApiClientFactory._configure_proxy(server_config, configuration)

        client = ApiClient(configuration=configuration)
        ApiClientFactory._add_headers(client, server_config)

        return client

    @staticmethod
    def _add_headers( client, server_config):
        for header_name, header_value in ApiClientFactory._sanitized_default_headers(server_config).items():
            client.set_default_header(header_name, header_value)
        client.user_agent = ApiClientFactory._user_agent(server_config)

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

        result = {}
        for header_key, header_value in default_headers.items():
            # we do this because we want to handle user-agent header separately
            # for client configuration and proxy header
            if header_key.lower() != USER_AGENT.lower():
                result[header_key] = header_value

        return result

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
