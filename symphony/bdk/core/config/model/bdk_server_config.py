class BdkServerConfig:
    """Base class for server and client configurations
    """
    DEFAULT_SCHEME: str = "https"
    DEFAULT_HTTPS_PORT: int = 443

    def __init__(self, scheme=None, port=None, context="",  host=None, **kwargs):
        self.scheme = scheme if scheme is not None else self.DEFAULT_SCHEME
        self.port = self._port = port if port is not None else self.DEFAULT_HTTPS_PORT
        self.context = context
        self.host = host

    def get_base_path(self) -> str:
        """Constructs the base path of the current config

        :return: scheme://host:port + formated_context
        :rtype: str
        """
        return self.scheme + "://" + self.host + self.get_port_as_string() + self.get_formatted_context()

    def get_formatted_context(self) -> str:
        """Formats the context field

        :return: "/" + context if the context is not empty
        :rtype str
        """
        local_context = self.context
        if local_context is None:
            return ""
        if local_context and local_context[0] != "/":
            return "/" + local_context
        if local_context and local_context.endswith("/"):
            return local_context[0:-1]
        return local_context

    def get_port_as_string(self) -> str:
        if self.port is not None:
            return ":" + str(self.port)
        else:
            return ""
