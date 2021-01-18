from symphony.bdk.core.config.model.bdk_server_config import BdkServerConfig


class BdkClientConfig(BdkServerConfig):

    def __init__(self, parent_config, config):
        self.parent_config = parent_config
        if config is not None:
            self._scheme = config.get("scheme") if "scheme" in config else None
            self._port = config.get("port") if "port" in config else None
            self._host = config.get("host") if "host" in config else None
            self._context = config.get("context") if "context" in config else None
        else:
            self._scheme = None
            self._port = None
            self._host = None
            self._context = None


    @property
    def scheme(self):
        return self.__self_or_parent(self._scheme, self.parent_config.scheme)

    @property
    def port(self):
        return self.__self_or_parent(self._port, self.parent_config.port)

    @property
    def host(self):
        return self.__self_or_parent(self._host, self.parent_config.host)

    @property
    def context(self):
        return self.__self_or_parent(self._context, self.parent_config.context)

    @property
    def proxy(self):
        return self.__self_or_parent(self._proxy, self.parent_config.proxy)

    def __self_or_parent(self, instance_value, parent_value):
        # Figure out how to get instance_value's attribute of parent_value class
        return instance_value if instance_value is not None else parent_value
