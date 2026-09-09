import os
import subprocess
import sys
import textwrap

import pytest

from symphony.bdk.core.config.loader import BdkConfigLoader
from tests.utils.resource_utils import get_config_resource_filepath

# YAML and JSON are both specified as UTF-8. Reading a config with the platform
# codec instead produced no error on a codepage that happens to map the bytes:
# the bot started with a mojibake proxy password and failed later against the
# proxy with an unrelated-looking error.
EXPECTED_PASSWORD = "sésame-café"
EXPECTED_USERNAME = "café-user"

# The importers run in a child interpreter with a legacy locale forced on, so
# the test is meaningful on a UTF-8 CI host too. Without this it passes whether
# or not the fix is present, everywhere the locale is already UTF-8.
LEGACY_LOCALE_ENV = {
    "PYTHONUTF8": "0",
    "PYTHONCOERCECLOCALE": "0",
    "LC_ALL": "C",
    "LANG": "C",
}

LOAD_SCRIPT = textwrap.dedent(
    """
    import json, sys
    from symphony.bdk.core.config.loader import BdkConfigLoader

    config = BdkConfigLoader.load_from_file(sys.argv[1])
    sys.stdout.buffer.write(
        json.dumps(
            {"username": config.proxy.username, "password": config.proxy.password},
            ensure_ascii=False,
        ).encode("utf-8")
    )
    """
)


@pytest.fixture(name="utf8_config_path", params=["config_utf8.json", "config_utf8.yaml"])
def fixture_utf8_config_path(request):
    return get_config_resource_filepath(request.param)


def test_load_from_file_reads_utf8_under_legacy_locale(utf8_config_path, tmp_path):
    """A UTF-8 config loads identically regardless of the host locale."""
    script = tmp_path / "load.py"
    script.write_text(LOAD_SCRIPT, encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(script), utf8_config_path],
        capture_output=True,
        env={**os.environ, **LEGACY_LOCALE_ENV},
    )

    # Catches the loud failure: on a locale that cannot map the bytes at all,
    # read_text raises and the bot never starts.
    assert completed.returncode == 0, completed.stderr.decode("utf-8", "replace")

    # Catches the silent one. Asserting on bytes decoded as UTF-8 is the point:
    # comparing strings that came back through the same broken default would
    # round-trip the mojibake and pass either way.
    import json

    loaded = json.loads(completed.stdout.decode("utf-8"))
    assert loaded["password"] == EXPECTED_PASSWORD
    assert loaded["username"] == EXPECTED_USERNAME


def test_load_from_file_matches_load_from_content(utf8_config_path):
    """The two entry points agree.

    load_from_content is handed already-decoded text and was always correct,
    so it serves as the oracle for what load_from_file should produce.
    """
    from pathlib import Path

    from_file = BdkConfigLoader.load_from_file(utf8_config_path)
    from_content = BdkConfigLoader.load_from_content(
        Path(utf8_config_path).read_text(encoding="utf-8")
    )

    assert from_file.proxy.password == from_content.proxy.password
    assert from_file.proxy.password == EXPECTED_PASSWORD


def test_ascii_config_is_unaffected():
    """The ASCII path the existing fixtures cover is unchanged.

    A control: this passes with and without the fix, so a failure here means
    the harness broke rather than the encoding handling.
    """
    config = BdkConfigLoader.load_from_file(get_config_resource_filepath("config.yaml"))
    assert config.bot.username == "youbot"
