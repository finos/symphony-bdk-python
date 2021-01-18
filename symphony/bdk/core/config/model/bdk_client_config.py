from symphony.bdk.core.config.model.bdk_server_config import BdkServerConfig


class BdkClientConfig(BdkServerConfig):
    """Class containing a client configuration

    :param parent_config: BdkConfig The parent configuration
    :param  config: dict Client configuration parameters
    """

    def __init__(self, parent_config, config):
        self.parent_config = parent_config
        if config is not None:
            self._scheme = config.get("scheme")
            self._port = config.get("port")
            self._host = config.get("host")
            self._context = config.get("context")
        else:
            self._scheme = None
            self._port = None
            self._host = None
            self._context = None

    @property
    def scheme(self):
        return self._self_or_parent(self._scheme, self.parent_config.scheme)

    @property
    def port(self):
        return self._self_or_parent(self._port, self.parent_config.port)

    @property
    def host(self):
        return self._self_or_parent(self._host, self.parent_config.host)

    @property
    def context(self):
        return self._self_or_parent(self._context, self.parent_config.context)

    @staticmethod
    def _self_or_parent(instance_value, parent_value):
        """Get the parent configuration field if the current client's field is not defined

        :param instance_value: current client field
        :param parent_value: parent configuration field
        :return:
        """
        return instance_value if instance_value is not None else parent_value
