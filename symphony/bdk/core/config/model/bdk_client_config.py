from symphony.bdk.core.config.model.bdk_server_config import BdkServerConfig, BdkProxyConfig


class BdkClientConfig(BdkServerConfig):
    """Class containing a client configuration:
    - scheme (e.g. 'https')
    - host
    - port
    - context (path to be appended after the port).
    This is used to build the URL when making HTTP calls.
    URL will be built as follows: {scheme}://{host}:{port}/{context}
    """

    def __init__(self, parent_config, config):
        """

        :param parent_config: the parent configuration of type BdkConfig
        :param config: client configuration parameters of type dict
        """
        if config is None:
            config = {}

        self._scheme = config.get("scheme")
        self._port = config.get("port")
        self._host = config.get("host")
        self._context = config.get("context")
        self._proxy = BdkProxyConfig(**config.get("proxy")) if "proxy" in config else None
        self._default_headers = config.get("defaultHeaders") if "defaultHeaders" in config else None
        self.parent_config = parent_config

    @property
    def scheme(self):
        """Return the applicable scheme: either the one configured at child level (e.g. 'pod') or at global level.

        :return: the applicable scheme (e.g. 'https')
        """
        return self._self_or_parent(self._scheme, self.parent_config.scheme)

    @property
    def port(self):
        """Return the applicable port: either the one configured at child level (e.g. 'pod') or at global level.

        :return: the applicable port (e.g. 443)
        """
        return self._self_or_parent(self._port, self.parent_config.port)

    @property
    def host(self):
        """Return the applicable host: either the one configured at child level (e.g. 'pod') or at global level.

        :return: the applicable host (e.g. 'acme.symphony.com')
        """
        return self._self_or_parent(self._host, self.parent_config.host)

    @property
    def context(self):
        """Return the applicable context path: either the one configured at child level (e.g. 'pod') or at global level.

        :return: the applicable context path
        """
        return self._self_or_parent(self._context, self.parent_config.context)

    @property
    def proxy(self):
        """Return the applicable proxy information: either the one configured at child level (e.g. 'pod')
        or at global level.

        :return: the applicable proxy information
        """
        return self._self_or_parent(self._proxy, self.parent_config.proxy)

    @property
    def default_headers(self):
        """Return the applicable default headers: either the one configured at child level (e.g. 'pod')
        or at global level.

        :return: the applicable default headers
        """
        return self._self_or_parent(self._default_headers, self.parent_config.default_headers)

    @staticmethod
    def _self_or_parent(instance_value, parent_value):
        """Get the parent configuration field if the current client's field is not defined

        :param instance_value: current client field
        :param parent_value: parent configuration field
        :return: the value at child level if set or at parent level otherwise
        """
        return instance_value if instance_value is not None else parent_value
