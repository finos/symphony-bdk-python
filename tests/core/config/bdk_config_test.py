from symphony.bdk.core.config.loader import BdkConfigLoader

from tests.utils.resource_utils import get_config_resource_filepath
import pytest

pk = '-----BEGIN RSA PRIVATE KEY-----\n'\
     '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\n'\
     '-----END RSA PRIVATE KEY-----'

cert = '-----BEGIN CERTIFICATE-----\n'\
       'ggEBAL5Z8cEbWs5jnXxWneP1nO9Hu6oCWErdK4aPDb/otarsMF0ZYmWKR3Urr1Fe\n'\
       'rTadMDHOFki40JPibkUxTmW0IfSV4Hw3QOordMtMyhLfGes9f45VrkSH74VjfsPa\n'\
       'kA+ku9qi4cl4xtL1Uve5wv7QZm55jSdvhIATPfiLjud3fkItHVOpP2Wh25fHdw8s\n'\
       'ggEBAL5Z8cEbWs5jnXxWneP1nO9Hu6oCWErdK4aPDb/otarsMF0ZYmWKR3Urr1Fe\n'\
       'rTadMDHOFki40JPibkUxTmW0IfSV4Hw3QOordMtMyhLfGes9f45VrkSH74VjfsPa\n'\
       'kA+ku9qi4cl4xtL1Uve5wv7QZm55jSdvhIATPfiLjud3fkItHVOpP2Wh25fHdw8s\n'\
       'ggEBAL5Z8cEbWs5jnXxWneP1nO9Hu6oCWErdK4aPDb/otarsMF0ZYmWKR3Urr1Fe\n'\
       'VsuuUAlA5h+vnYsUwsYwVQYIKwYBBQUHAQEESTBHMCEGCCsGAQUFBzABhhVodHRw\n'\
       'VsuuUAlA5h+vnYsUwsYwVQYIKwYBBQUHAQEESTBHMCEGCCsGAQUFBzABhhVodHRw\n'\
       'LNxzkeincwlfIHYAVpUyPrysCHSY5rHV3CSDxDy0fcbf7oGBqUTjGY0+Wmkg0KJ4\n'\
       'l+6DxwmfSi14sGD23WCgk+yluzkCAwEAAaOCAmUwggJhMA4GA1UdDwEB/wQEAwIF\n'\
       'oDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwDAYDVR0TAQH/BAIwADAd\n'\
       'BgNVHQ4EFgQUh8wp9gvtkSRo1k7xjb281MLiEIkwHwYDVR0jBBgwFoAUFC6zF7dY\n'\
       'Oi8vcjMuby5sZW5jci5vcmcwIgYIKwYBBQUHMAKGFmh0dHA6Ly9yMy5pLmxlbmNy\n'\
       'oDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwDAYDVR0TAQH/BAIwADAd\n'\
       'oDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwDAYDVR0TAQH/BAIwADAd\n'\
       'oDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwDAYDVR0TAQH/BAIwADAd\n'\
       'oDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwDAYDVR0TAQH/BAIwADAd\n'\
       'oDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwDAYDVR0TAQH/BAIwADAd\n'\
       'oDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwDAYDVR0TAQH/BAIwADAd\n'\
       'oDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwDAYDVR0TAQH/BAIwADAd\n'\
       'oDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwDAYDVR0TAQH/BAIwADAd\n'\
       'wQLPKiR1TuBO9R09FHnAVbRwMA0GCSqGSIb3DQEBCwUAA4IBAQB8xXruO9Dy+4lS\n'\
       'wQLPKiR1TuBO9R09FHnAVbRwMA0GCSqGSIb3DQEBCwUAA4IBAQB8xXruO9Dy+4lS\n'\
       'gpNSaoiNs9WXFpTeReX1Iw6ND1HSASbC4gRenr8jJvq4cHMdSEmlz3lMyG9wpt3N\n'\
       'GZ/FdshGJc24wexIrATlpTE14fqxOv/Lt89gkkYyJ7f4YOipa/yBslrZC0ZfHEiN\n'\
       'EJQWnZ7F\n'\
       '-----END CERTIFICATE-----'

@pytest.fixture(params=["config.json", "config.yaml"])
def simple_config_path(request):
    return get_config_resource_filepath(request.param)

def test_update_privateKey(simple_config_path):
    config = BdkConfigLoader.load_from_file(simple_config_path)
    config.bot.private_key.setContent(rsa_key_content=pk)
    assert config.bot.private_key.content == pk
    assert config.bot.private_key.path is None

def test_update_certificate(simple_config_path):
    config = BdkConfigLoader.load_from_file(simple_config_path)
    config.bot.certificate.setContent(certificate_content=cert)
    assert config.bot.certificate.content == cert
    assert config.bot.certificate.path is None

