import re
from unittest.mock import patch

import pytest

from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.config.model.bdk_server_config import BdkProxyConfig
from symphony.bdk.core.config.model.bdk_ssl_config import BdkSslConfig

HOST = "acme.symphony.com"


@pytest.fixture()
def config():
    return BdkConfig(host=HOST)


@pytest.mark.asyncio
async def test_host_configured(config):
    client_factory = ApiClientFactory(config)

    assert_host_configured_only(client_factory.get_pod_client(), "/pod")
    assert_host_configured_only(client_factory.get_login_client(), "/login")
    assert_host_configured_only(client_factory.get_agent_client(), "/agent")
    assert_host_configured_only(client_factory.get_session_auth_client(), "/sessionauth")
    assert_host_configured_only(client_factory.get_relay_client(), "/relay")


@pytest.mark.asyncio
async def test_proxy_configured(config):
    proxy_host = "proxy.com"
    proxy_port = 1234
    config.proxy = BdkProxyConfig(proxy_host, proxy_port)
    client_factory = ApiClientFactory(config)

    assert_host_and_proxy_configured(client_factory.get_pod_client(), "/pod", proxy_host, proxy_port)
    assert_host_and_proxy_configured(client_factory.get_login_client(), "/login", proxy_host, proxy_port)
    assert_host_and_proxy_configured(client_factory.get_agent_client(), "/agent", proxy_host, proxy_port)
    assert_host_and_proxy_configured(client_factory.get_session_auth_client(), "/sessionauth", proxy_host, proxy_port)
    assert_host_and_proxy_configured(client_factory.get_relay_client(), "/relay", proxy_host, proxy_port)


@pytest.mark.asyncio
async def test_proxy_credentials_configured(config):
    proxy_host = "proxy.com"
    proxy_port = 1234
    config.proxy = BdkProxyConfig(proxy_host, proxy_port, "user", "pass")
    client_factory = ApiClientFactory(config)

    assert_host_and_proxy_credentials_configured(client_factory.get_pod_client(), "/pod", proxy_host, proxy_port)
    assert_host_and_proxy_credentials_configured(client_factory.get_login_client(), "/login", proxy_host, proxy_port)
    assert_host_and_proxy_credentials_configured(client_factory.get_agent_client(), "/agent", proxy_host, proxy_port)
    assert_host_and_proxy_credentials_configured(client_factory.get_session_auth_client(), "/sessionauth", proxy_host,
                                                 proxy_port)
    assert_host_and_proxy_credentials_configured(client_factory.get_relay_client(), "/relay", proxy_host, proxy_port)


def test_trust_store_configured(config):
    with patch("symphony.bdk.gen.rest.RESTClientObject"):
        truststore_path = "/path/to/truststore.pem"
        config.ssl = BdkSslConfig({"trustStore": {"path": truststore_path}})

        client_factory = ApiClientFactory(config)

        assert client_factory.get_pod_client().configuration.ssl_ca_cert == truststore_path


def assert_host_configured_only(client, url_suffix):
    configuration = client.configuration

    assert configuration.host == f"https://{HOST}:443{url_suffix}"
    assert_user_agent_configured(client.user_agent)

    assert configuration.proxy is None
    assert configuration.proxy_headers is None


def assert_host_and_proxy_configured(client, url_suffix, proxy_host, proxy_port):
    configuration = client.configuration

    assert configuration.host == f"https://{HOST}:443{url_suffix}"
    assert configuration.proxy == f"http://{proxy_host}:{proxy_port}"
    assert_user_agent_configured(client.user_agent)

    assert "proxy-authorization" not in configuration.proxy_headers
    assert "user-agent" in configuration.proxy_headers
    assert_user_agent_configured(configuration.proxy_headers["user-agent"])


def assert_host_and_proxy_credentials_configured(client, url_suffix, proxy_host, proxy_port):
    configuration = client.configuration

    assert configuration.host == f"https://{HOST}:443{url_suffix}"
    assert configuration.proxy == f"http://{proxy_host}:{proxy_port}"
    assert_user_agent_configured(client.user_agent)

    assert "proxy-authorization" in configuration.proxy_headers
    assert "user-agent" in configuration.proxy_headers
    assert_user_agent_configured(configuration.proxy_headers["user-agent"])


def assert_user_agent_configured(user_agent):
    assert re.match(r"^Symphony-BDK-Python/\S+ Python/3\.\S+$", user_agent) is not None
