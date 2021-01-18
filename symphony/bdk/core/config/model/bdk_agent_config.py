from symphony.bdk.core.config.model.bdk_client_config import BdkClientConfig


class BdkAgentConfig(BdkClientConfig):

    def __init__(self, parent_config, agent_config):
            super().__init__(parent_config, agent_config)