from symphony.bdk.core.config.model.bdk_server_config import BdkProxyConfig
from tests.utils.resource_utils import get_config_resource_filepath
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.config.exception import BdkConfigException

import os
import pytest
from pathlib import Path
import uuid


@pytest.fixture(params=["config.json", "config.yaml"])
def simple_config_path(request):
    return get_config_resource_filepath(request.param)


@pytest.fixture(params=["config_global.json", "config_global.yaml"])
def global_config_path(request):
    return get_config_resource_filepath(request.param)


@pytest.fixture(params=["/wrong_path/config.json", "/wrong_path/wrong_extension.something"])
def wrong_path(request):
    return request.param


def test_load_from_file(simple_config_path):
    config = BdkConfigLoader.load_from_file(simple_config_path)
    assert config.bot.username == "youbot"


def test_load_from_content(simple_config_path):
    config_path = Path(simple_config_path)
    content = config_path.read_text()
    config = BdkConfigLoader.load_from_content(content)
    assert config.bot.username == "youbot"


def test_load_from_file_not_found(wrong_path):
    fail_error_message = f"Config file has not been found at: {Path(wrong_path).absolute()}"
    with pytest.raises(BdkConfigException, match=fail_error_message):
        config = BdkConfigLoader.load_from_file(wrong_path)


@pytest.mark.skipif(os.environ.get("CIRCLECI") == "true",
                    reason="CircleCI does not allow to create file in the home directory")
def test_load_from_symphony_directory(simple_config_path):
    tmp_config_filename = str(uuid.uuid4()) + "-config.yaml"
    tmp_config_path = Path.home() / ".symphony" / tmp_config_filename
    tmp_config_path.touch(exist_ok=True)
    resource_config_content = Path(simple_config_path).read_text()
    tmp_config_path.write_text(resource_config_content)
    config = BdkConfigLoader.load_from_symphony_dir(tmp_config_filename)
    assert config.bot.username == "youbot"


def test_load_client_global_config(global_config_path):
    config = BdkConfigLoader.load_from_file(global_config_path)
    assert config.pod.scheme == "https"
    assert config.pod.host == "diff-pod.symphony.com"
    assert config.pod.port == 8443
    assert config.pod.context == "context"

    assert config.scheme == "https"

    assert config.agent.scheme == "https"
    assert config.agent.host == "devx1.symphony.com"
    assert config.agent.port == 443
    assert config.agent.get_formatted_context() == "/context"

    assert config.key_manager.scheme == "https"
    assert config.key_manager.host == "devx1.symphony.com"
    assert config.key_manager.port == 8443
    assert config.key_manager.get_formatted_context() == "/diff-context"

    assert config.session_auth.scheme == "http"
    assert config.session_auth.host == "devx1.symphony.com"
    assert config.session_auth.port == 8443
    assert config.session_auth.context == "context"


def test_load_proxy_defined_at_global_level():
    config = BdkConfigLoader.load_from_file(get_config_resource_filepath("config_global_proxy.yaml"))

    assert config.proxy.host == "proxy.symphony.com"
    assert config.proxy.port == 1234
    assert config.proxy.username == "proxyuser"
    assert config.proxy.password == "proxypass"

    assert config.agent.proxy == config.proxy
    assert config.pod.proxy == config.proxy
    assert config.key_manager.proxy == config.proxy
    assert config.session_auth.proxy == config.proxy


def test_load_proxy_defined_at_global_and_child_level():
    config = BdkConfigLoader.load_from_file(get_config_resource_filepath("config_proxy_global_child.yaml"))

    assert config.proxy.host == "proxy.symphony.com"
    assert config.proxy.port == 1234
    assert config.proxy.username == "proxyuser"
    assert config.proxy.password == "proxypass"

    assert config.pod.proxy == config.proxy
    assert config.key_manager.proxy == config.proxy
    assert config.session_auth.proxy == config.proxy

    assert config.agent.proxy.host == "agent-proxy.symphony.com"
    assert config.agent.proxy.port == 5678
    assert config.agent.proxy.username is None
    assert config.agent.proxy.password is None


def test_load_proxy_defined_at_child_level_only():
    config = BdkConfigLoader.load_from_file(get_config_resource_filepath("config_proxy_child_only.yaml"))

    assert config.proxy is None
    assert config.pod.proxy is None
    assert config.key_manager.proxy is None
    assert config.session_auth.proxy is None

    assert config.agent.proxy.host == "agent-proxy.symphony.com"
    assert config.agent.proxy.port == 5678
    assert config.agent.proxy.username is None
    assert config.agent.proxy.password is None
