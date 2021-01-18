class BdkServerConfig:
    """Base class for server and client configurations
    """
    _DEFAULT_SCHEME: str = "https"
    _DEFAULT_HTTPS_PORT: int = 443

    def __init__(self, scheme=_DEFAULT_SCHEME, port=_DEFAULT_HTTPS_PORT, context="",  host=None, **kwargs):
        self._scheme = scheme
        self._port = port
        self.context = context
        self._host = host

    def get_base_path(self) -> str:
        """Constructs the base path of the current config

        :return: scheme://host:port + formated_context
        :rtype: str
        """
        return self.scheme + "://" + self.host + self.get_port_as_string() + self.get_formated_context()

    def get_formated_context(self) -> str:
        """Formats the context field

        :return: "/" + context if the context is not empty
        :rtype str
        """
        local_context = self.context
        if local_context == None:
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

    @property
    def scheme(self):
        return self._scheme

    @scheme.setter
    def scheme(self, value):
        self._scheme = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def proxy(self):
        return self._proxy

    @proxy.setter
    def proxy(self, value):
        self._proxy = value

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
