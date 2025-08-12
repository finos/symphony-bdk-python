import pytest

from symphony.bdk.core.activity.parsing.arguments import Arguments
from symphony.bdk.core.activity.parsing.message_entities import Cashtag, Hashtag, Mention


@pytest.fixture(name="arguments_dict")
def fixture_arguments_dict():
    return {
        "string_arg": "string_arg_value",
        "mention_arg": Mention("@Jane Dow", 12345),
        "hashtag_arg": Hashtag("#my_hashtag", "my_hashtag"),
        "cashtag_arg": Cashtag("$my_cashtag", "my_cashtag"),
    }


@pytest.fixture(name="arguments")
def fixture_arguments(arguments_dict):
    return Arguments(arguments_dict)


def test_get_argument_names(arguments):
    assert ["string_arg", "mention_arg", "hashtag_arg", "cashtag_arg"] == list(
        arguments.get_argument_names()
    )


def test_get_argument(arguments):
    assert arguments.get("string_arg") == "string_arg_value"
    assert arguments.get("mention_arg") == Mention("@Jane Dow", 12345)
    assert arguments.get("hashtag_arg") == Hashtag("#my_hashtag", "my_hashtag")
    assert arguments.get("cashtag_arg") == Cashtag("$my_cashtag", "my_cashtag")
    assert arguments.get("not_found") is None


def test_get_as_string(arguments):
    assert arguments.get_as_string("string_arg") == "string_arg_value"
    assert arguments.get_as_string("mention_arg") == "@Jane Dow"
    assert arguments.get_as_string("hashtag_arg") == "#my_hashtag"
    assert arguments.get_as_string("cashtag_arg") == "$my_cashtag"
    assert arguments.get_as_string("not_found") is None


def test_get_string(arguments):
    assert arguments.get_string("string_arg") == "string_arg_value"
    assert arguments.get_string("mention_arg") is None
    assert arguments.get_string("hashtag_arg") is None
    assert arguments.get_string("cashtag_arg") is None
    assert arguments.get_string("not_found") is None


def test_get_mention(arguments):
    assert arguments.get_mention("mention_arg") == Mention("@Jane Dow", 12345)
    assert arguments.get_mention("string_arg") is None
    assert arguments.get_mention("hashtag_arg") is None
    assert arguments.get_mention("cashtag_arg") is None
    assert arguments.get_mention("not_found") is None


def test_get_hashtag(arguments):
    assert arguments.get_hashtag("hashtag_arg") == Hashtag("#my_hashtag", "my_hashtag")
    assert arguments.get_hashtag("string_arg") is None
    assert arguments.get_hashtag("mention_arg") is None
    assert arguments.get_hashtag("cashtag_arg") is None
    assert arguments.get_hashtag("not_found") is None


def test_get_cashtag(arguments):
    assert arguments.get_cashtag("cashtag_arg") == Cashtag("$my_cashtag", "my_cashtag")
    assert arguments.get_cashtag("string_arg") is None
    assert arguments.get_cashtag("mention_arg") is None
    assert arguments.get_cashtag("hashtag_arg") is None
    assert arguments.get_cashtag("not_found") is None
