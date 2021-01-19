from symphony.bdk.core.config.model.bdk_server_config import BdkServerConfig


def test_get_base_path():
    config = BdkServerConfig(scheme="https", host="dev.symphony.com", port=123, context="context")
    assert config.get_base_path() == "https://dev.symphony.com:123/context"


def test_wrong_input_types():
    config = BdkServerConfig(scheme=2, host=2, port="port", context=2)
    assert config.get_formatted_context() == ""
    assert config.get_base_path() == "2://2:port"


def test_get_port_as_string():
    config = BdkServerConfig(port=None)
    assert config.get_port_as_string() == f":{config.DEFAULT_HTTPS_PORT}"

    config = BdkServerConfig(port=2)
    assert config.get_port_as_string() == ":2"

    config.port = "884"
    assert config.get_port_as_string() == ":884"

    config.port = None
    assert config.get_port_as_string() == ""
