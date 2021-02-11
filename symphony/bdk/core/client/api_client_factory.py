"""Module containing the ApiClientFactory class.
"""
import urllib3

from symphony.bdk.gen.configuration import Configuration
from symphony.bdk.gen.api_client import ApiClient


class ApiClientFactory:
    """Factory responsible for creating ApiClient instances for each main Symphony's components.
    """

    def __init__(self, config):
        self._config = config
        self._login_client = self._get_api_client(self._config.pod, '/login')
        self._pod_client = self._get_api_client(self._config.pod, '/pod')
        self._relay_client = self._get_api_client(self._config.key_manager, '/relay')
        self._agent_client = self._get_api_client(self._config.session_auth, '/agent')
        self._session_auth_client = self._get_api_client(self._config.session_auth, '/sessionauth')

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
            self._configure_proxy(server_config.proxy, configuration)

        return ApiClient(configuration=configuration)

    @staticmethod
    def _configure_proxy(proxy_config, configuration):
        configuration.proxy = proxy_config.get_url()

        if proxy_config.are_credentials_defined():
            configuration.proxy_headers = urllib3.util.make_headers(proxy_basic_auth=proxy_config.get_credentials())
