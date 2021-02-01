from symphony.bdk.core.config.model.bdk_datafeed_config import BdkDatafeedConfig
from pathlib import Path
import pytest


@pytest.fixture(params=["v1", 25, True])
def datafeed_version(request):
    return request.param


# maybe can find an alternative to cucumber
def test_empty_datafeed_config():
    datafeed_config = BdkDatafeedConfig(None)
    assert datafeed_config.version == "v1"

    assert datafeed_config.id_file_path == ""
    assert isinstance(datafeed_config.get_id_file_path(), Path)
    assert datafeed_config.get_id_file_path() == Path(".")


def test_version(datafeed_version):
    datafeed_config = BdkDatafeedConfig({"version": datafeed_version})
    assert datafeed_config.version == datafeed_version


def test_get_id_file_path():
    datafeed_config = BdkDatafeedConfig({})
    assert datafeed_config.get_id_file_path() == Path(".")

    datafeed_config.id_file_path = Path("dummy_path").resolve()
    assert datafeed_config.id_file_path == Path("dummy_path").resolve()
