from symphony.bdk.gen.configuration import Configuration
from symphony.bdk.gen.api_client import ApiClient


class ApiClientFactory:
    """
    Factory responsible for creating ApiClient instances for each main Symphony's components.
    """

    def __init__(self, config):
        self._config = config

    def get_login_client(self) -> ApiClient:
        """
        Returns a fully initialized ApiClient for Login API.

        Returns: a new ApiClient instance for Login API.

        """
        return self.__get_api_client(self._config.pod, '/login')

    def get_pod_client(self) -> ApiClient:
        """
        Returns a fully initialized ApiClient for Pod API.

        Returns: a new ApiClient instance for Pod API.

        """
        return self.__get_api_client(self._config.key_manager, '/pod')

    def get_relay_client(self) -> ApiClient:
        """
        Returns a fully initialized ApiClient for Key Manager API.

        Returns: a new ApiClient instance for Key Manager API.

        """
        return self.__get_api_client(self._config.key_manager, '/relay')

    def get_session_auth_client(self) -> ApiClient:
        """
        Returns a fully initialized ApiClient for Session Auth API.

        Returns: a new ApiClient instance for Session Auth API.

        """
        return self.__get_api_client(self._config.session_auth, '/sessionauth')

    def get_agent_client(self) -> ApiClient:
        """
        Returns a fully initialized ApiClient for Agent API.

        Returns: a new ApiClient instance for Agent API.

        """
        return self.__get_api_client(self._config.agent, '/agent')

    @staticmethod
    def __get_api_client(server_config, context='') -> ApiClient:
        path = server_config.get_base_path() + context
        configuration = Configuration(host=path)
        return ApiClient(configuration=configuration)
