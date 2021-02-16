from symphony.bdk.core.config.model.bdk_datafeed_config import BdkDatafeedConfig, DF_V1
from pathlib import Path
import pytest


@pytest.fixture(params=["v1"])
def datafeed_version(request):
    return request.param


def test_empty_datafeed_config():
    datafeed_config = BdkDatafeedConfig(None)
    assert datafeed_config.version == "v1"

    assert datafeed_config.id_file_path == ""
    assert isinstance(datafeed_config.get_id_file_path(), Path)
    assert datafeed_config.get_id_file_path().resolve() == Path(".").resolve()


def test_version_should_default_on_v1(datafeed_version):
    datafeed_config = BdkDatafeedConfig({"version": datafeed_version})
    assert datafeed_config.version == DF_V1


def test_get_id_file_path():
    datafeed_config = BdkDatafeedConfig({"idFilePath": Path("dummy_path")})
    assert datafeed_config.get_id_file_path().resolve() == Path("dummy_path").resolve()
