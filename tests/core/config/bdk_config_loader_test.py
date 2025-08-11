import os
import re
import uuid
from pathlib import Path

import pytest

from symphony.bdk.core.config.exception import BdkConfigError
from symphony.bdk.core.config.loader import BdkConfigLoader
from tests.utils.resource_utils import get_config_resource_filepath


@pytest.fixture(name="simple_config_path", params=["config.json", "config.yaml"])
def fixture_simple_config_path(request):
    return get_config_resource_filepath(request.param)


@pytest.fixture(
    name="global_config_path", params=["config_global.json", "config_global.yaml"]
)
def fixture_global_config_path(request):
    return get_config_resource_filepath(request.param)


@pytest.fixture(
    name="wrong_path",
    params=["/wrong_path/config.json", "/wrong_path/wrong_extension.something"],
)
def fixture_wrong_path(request):
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
    fail_error_message = (
        f"Config file has not been found at: {Path(wrong_path).absolute()}"
    )
    with pytest.raises(BdkConfigError, match=re.escape(fail_error_message)):
        BdkConfigLoader.load_from_file(wrong_path)


@pytest.mark.skipif(
    os.environ.get("CI") == "true",
    reason="GitHub actions does not allow to create file in the home directory",
)
def test_load_from_symphony_directory(simple_config_path):
    tmp_config_filename = str(uuid.uuid4()) + "-config.yaml"
    tmp_config_path = Path.home() / ".symphony" / tmp_config_filename
    tmp_config_path.touch(exist_ok=True)
    resource_config_content = Path(simple_config_path).read_text()
    tmp_config_path.write_text(resource_config_content)
    config = BdkConfigLoader.load_from_symphony_dir(tmp_config_filename)
    assert config.bot.username == "youbot"


def test_load_client_global_config(global_config_path):
    expected_scheme = "https"
    expected_host = "devx1.symphony.com"
    expected_default_headers = {
        "user-agent": "custom-user-agent",
        "header-key": "header-value",
    }

    config = BdkConfigLoader.load_from_file(global_config_path)

    assert config.scheme == expected_scheme
    assert config.host == expected_host
    assert config.port == 8443
    assert config.default_headers == expected_default_headers

    assert config.pod.scheme == expected_scheme
    assert config.pod.host == "diff-pod.symphony.com"
    assert config.pod.port == 8443
    assert config.pod.context == "context"
    assert config.pod.default_headers == expected_default_headers

    assert config.scheme == expected_scheme

    assert config.agent.scheme == expected_scheme
    assert config.agent.host == expected_host
    assert config.agent.port == 443
    assert config.agent.get_formatted_context() == "/context"
    assert config.agent.default_headers == expected_default_headers

    assert config.key_manager.scheme == expected_scheme
    assert config.key_manager.host == expected_host
    assert config.key_manager.port == 8443
    assert config.key_manager.get_formatted_context() == "/diff-context"
    assert config.key_manager.default_headers == expected_default_headers

    assert config.session_auth.scheme == "http"
    assert config.session_auth.host == expected_host
    assert config.session_auth.port == 8443
    assert config.session_auth.context == "context"
    assert config.session_auth.default_headers == expected_default_headers


def test_load_proxy_defined_at_global_level():
    config = BdkConfigLoader.load_from_file(
        get_config_resource_filepath("config_global_proxy.yaml")
    )

    assert config.proxy.host == "proxy.symphony.com"
    assert config.proxy.port == 1234
    assert config.proxy.username == "proxyuser"
    assert config.proxy.password == "proxypass"

    assert config.agent.proxy == config.proxy
    assert config.pod.proxy == config.proxy
    assert config.key_manager.proxy == config.proxy
    assert config.session_auth.proxy == config.proxy


def test_load_proxy_defined_at_global_and_child_level():
    config = BdkConfigLoader.load_from_file(
        get_config_resource_filepath("config_proxy_global_child.yaml")
    )

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
    config = BdkConfigLoader.load_from_file(
        get_config_resource_filepath("config_proxy_child_only.yaml")
    )

    assert config.proxy is None
    assert config.pod.proxy is None
    assert config.key_manager.proxy is None
    assert config.session_auth.proxy is None

    assert config.agent.proxy.host == "agent-proxy.symphony.com"
    assert config.agent.proxy.port == 5678
    assert config.agent.proxy.username is None
    assert config.agent.proxy.password is None


def test_load_default_headers_defined_at_child_level_only():
    config = BdkConfigLoader.load_from_file(
        get_config_resource_filepath("config_headers_child_only.yaml")
    )

    assert config.default_headers is None
    assert config.pod.default_headers is None
    assert config.key_manager.default_headers is None
    assert config.session_auth.default_headers is None
    assert config.agent.default_headers == {
        "user-agent": "custom-user-agent",
        "header-key": "header-value",
    }


def test_load_default_headers_defined_at_global_and_child_level():
    global_headers = {
        "user-agent": "global-user-agent",
        "header-key": "global-header-value",
    }

    config = BdkConfigLoader.load_from_file(
        get_config_resource_filepath("config_headers_global_child.yaml")
    )

    assert config.default_headers == global_headers
    assert config.pod.default_headers == global_headers
    assert config.key_manager.default_headers == global_headers
    assert config.session_auth.default_headers == global_headers
    assert config.agent.default_headers == {
        "user-agent": "agent-user-agent",
        "header-key": "agent-header-value",
    }
