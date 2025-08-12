import pytest

from symphony.bdk.gen import Configuration, rest


@pytest.mark.asyncio
async def test_system_certs_are_loaded():
    rest_client = rest.RESTClientObject(Configuration())

    # Calling an URL with a valid HTTPS cert
    response = await rest_client.GET("https://google.fr")

    assert response.status == 200
