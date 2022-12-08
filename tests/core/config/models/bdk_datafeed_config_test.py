from pathlib import Path

import pytest

from symphony.bdk.core.config.model.bdk_datafeed_config import BdkDatafeedConfig, DF_V1


@pytest.fixture(name="datafeed_version", params=["v1"])
def fixture_datafeed_version(request):
    return request.param


def test_empty_datafeed_config():
    datafeed_config = BdkDatafeedConfig(None)
    assert datafeed_config.version == "v2"

    assert datafeed_config.id_file_path == ""
    assert isinstance(datafeed_config.get_id_file_path(), Path)
    assert datafeed_config.get_id_file_path().resolve() == Path(".").resolve()


def test_version_should_default_on_v1(datafeed_version):
    datafeed_config = BdkDatafeedConfig({"version": datafeed_version})
    assert datafeed_config.version == DF_V1


def test_get_id_file_path():
    datafeed_config = BdkDatafeedConfig({"idFilePath": Path("dummy_path")})
    assert datafeed_config.get_id_file_path().resolve() == Path("dummy_path").resolve()
    assert datafeed_config.tag is None


def test_config_with_tag():
    datafeed_config = BdkDatafeedConfig({"idFilePath": Path("dummy_path"), "tag": "tag"})
    assert datafeed_config.get_id_file_path().resolve() == Path("dummy_path").resolve()
    assert datafeed_config.tag == "tag"
