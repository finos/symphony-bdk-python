class BdkServerConfig:
    """Base class for server and client configurations"""
    DEFAULT_SCHEME: str = "https"
    DEFAULT_HTTPS_PORT: int = 443

    def __init__(self, scheme=None, port=None, context="", host=None, proxy=None, default_headers=None):
        self.scheme = scheme if scheme is not None else self.DEFAULT_SCHEME
        self.port = self.port = port if port is not None else self.DEFAULT_HTTPS_PORT
        self.context = context
        self.host = host
        self.proxy = BdkProxyConfig(**proxy) if proxy is not None else None
        self.default_headers = default_headers

    def get_base_path(self) -> str:
        """Constructs the base path of the current config

        :return: scheme://host:port + formatted_context
        :rtype: str
        """
        return f"{self.scheme}://{self.host}{self.get_port_as_string()}{self.get_formatted_context()}"

    def get_formatted_context(self) -> str:
        """Formats the context field

        :return: "/" + context if the context is not empty
        :rtype: str
        """
        local_context = self.context
        if local_context is None or not isinstance(local_context, str):
            return ""
        if local_context and local_context[0] != "/":
            return "/" + local_context
        if local_context and local_context.endswith("/"):
            return local_context[0:-1]
        return local_context

    def get_port_as_string(self) -> str:
        """

        :return: the port information to be appended to the built URL
        """
        return ":" + str(self.port) if self.port else ""


class BdkProxyConfig:
    """Class to configure a proxy with a host, port and optional proxy credentials"""

    def __init__(self, host, port, username=None, password=None):
        """

        :param host: host of the proxy (mandatory)
        :param port: port of the proxy (mandatory)
        :param username: username for proxy basic authentication (optional)
        :param password: password for proxy basic authentication (optional, must be not None if username specified)
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def get_url(self):
        """Builds the proxy URL.

        :return: the URL of the http proxy to target
        """
        return f"http://{self.host}:{self.port}"

    def are_credentials_defined(self):
        """Check if proxy credentials were set

        :return: True if username and password set
        """
        return self.username and self.password is not None

    def get_credentials(self):
        """Builds the credentials information to pass to the proxy-authorization header before base64 encoding.

        :return: username + ":" + password
        """
        return f"{self.username}:{self.password}"
