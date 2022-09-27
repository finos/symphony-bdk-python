import pytest

from symphony.bdk.core.activity.parsing.message_entities import Cashtag, Hashtag, Mention
from symphony.bdk.core.activity.parsing.match_result import MatchResult
from symphony.bdk.core.activity.parsing.slash_command_pattern import SlashCommandPattern
from symphony.bdk.core.activity.parsing.command_token import StaticCommandToken, StringArgumentCommandToken, \
    HashArgumentCommandToken, CashArgumentCommandToken, MentionArgumentCommandToken
from symphony.bdk.gen.agent_model.v4_message import V4Message
from tests.core.activity.parsing.input_tokenizer_test import build_v4_message


def test_slash_command_empty_string():
    pattern = SlashCommandPattern("")

    assert pattern.tokens == []
    assert pattern.get_match_result(build_v4_message("")).is_matching
    assert not pattern.get_match_result(build_v4_message("/command")).is_matching


def test_slash_command_one_static_string():
    pattern = SlashCommandPattern("/command")

    assert pattern.tokens == [StaticCommandToken("/command")]
    assert pattern.tokens[0].pattern == "^/command$"
    assert pattern.get_match_result(build_v4_message("/command")).is_matching
    assert pattern.get_match_result(build_v4_message(" /command ")).is_matching
    assert not pattern.get_match_result(build_v4_message("/command arg")).is_matching


def test_slash_command_one_static_string_with_spaces():
    pattern = SlashCommandPattern(" /command ")

    assert pattern.tokens == [StaticCommandToken("/command")]
    assert pattern.tokens[0].pattern == "^/command$"
    assert pattern.get_match_result(build_v4_message("/command")).is_matching
    assert pattern.get_match_result(build_v4_message(" /command ")).is_matching
    assert not pattern.get_match_result(build_v4_message("/command arg")).is_matching


def test_slash_command_two_static_strings():
    pattern = SlashCommandPattern("/command command2")

    assert pattern.tokens == [StaticCommandToken("/command"), StaticCommandToken("command2")]
    assert pattern.tokens[0].pattern == "^/command$"
    assert pattern.tokens[1].pattern == "^command2$"

    assert not pattern.get_match_result(build_v4_message("")).is_matching
    assert not pattern.get_match_result(build_v4_message("/command")).is_matching
    assert not pattern.get_match_result(build_v4_message("/command command3")).is_matching
    assert not pattern.get_match_result(build_v4_message("/command command2 command3")).is_matching
    assert pattern.get_match_result(build_v4_message("/command command2")).is_matching
    assert pattern.get_match_result(build_v4_message("/command command2 ")).is_matching


def test_slash_command_two_static_strings_with_spaces():
    pattern = SlashCommandPattern(" /command command2 ")

    assert pattern.tokens == [StaticCommandToken("/command"), StaticCommandToken("command2")]
    assert pattern.tokens[0].pattern == "^/command$"
    assert pattern.tokens[1].pattern == "^command2$"

    assert not pattern.get_match_result(build_v4_message("")).is_matching
    assert not pattern.get_match_result(build_v4_message("/command")).is_matching
    assert not pattern.get_match_result(build_v4_message("/command command3")).is_matching
    assert not pattern.get_match_result(build_v4_message("/command command2 command3")).is_matching
    assert pattern.get_match_result(build_v4_message("/command command2")).is_matching
    assert pattern.get_match_result(build_v4_message("/command command2 ")).is_matching


def test_slash_command_with_two_string_arguments():
    pattern = SlashCommandPattern("/command {arg1} {arg2}")

    assert pattern.tokens == [StaticCommandToken("/command"), StringArgumentCommandToken("{arg1}"),
                              StringArgumentCommandToken("{arg2}")]
    assert pattern.tokens[0].pattern == "^/command$"
    assert pattern.tokens[1].arg_name == "arg1"
    assert pattern.tokens[2].arg_name == "arg2"

    assert not pattern.get_match_result(build_v4_message("")).is_matching
    assert not pattern.get_match_result(build_v4_message("/command")).is_matching
    assert not pattern.get_match_result(build_v4_message("/command arg1")).is_matching
    assert pattern.get_match_result(build_v4_message("/command arg1 arg2")).is_matching
    assert pattern.get_match_result(build_v4_message(" /command arg1 arg2 ")).is_matching


def test_slash_command_bad_string_command_argument():
    with pytest.raises(ValueError, match="Argument name is not valid"):
        SlashCommandPattern("{&}")


def test_slash_command_bad_hash_command_argument():
    with pytest.raises(ValueError, match="Argument name is not valid"):
        SlashCommandPattern("{##}")


def test_slash_command_bad_cash_command_argument():
    with pytest.raises(ValueError, match="Argument name is not valid"):
        SlashCommandPattern("{$$}")


def test_slash_command_static_argument_and_string_argument_glued():
    with pytest.raises(ValueError, match="Invalid pattern syntax"):
        SlashCommandPattern("/command{arg}")


def test_slash_command_two_arguments_glued():
    with pytest.raises(ValueError, match="Argument name is not valid"):
        SlashCommandPattern("{arg1}{arg2}")


def test_slash_command_two_arguments_same_name():
    with pytest.raises(ValueError, match="Argument names must be unique"):
        SlashCommandPattern("/command {arg} {arg}")


def test_slash_command_different_argument_types_same_name():
    with pytest.raises(ValueError, match="Argument names must be unique"):
        SlashCommandPattern("/command {@arg} {#arg}")


def test_slash_command_bad_mention_command_argument():
    with pytest.raises(ValueError, match="Argument name is not valid"):
        SlashCommandPattern("{@@}")


def test_string_argument_command():
    pattern = SlashCommandPattern("/command {string_arg} {@mention} {#hashtag} {$cashtag}")
    assert pattern.tokens == [StaticCommandToken("/command"), StringArgumentCommandToken("{string_arg}"),
                              MentionArgumentCommandToken("{@mention}"), HashArgumentCommandToken("{#hashtag}"),
                              CashArgumentCommandToken("{$cashtag}")]

    assert pattern.tokens[0].pattern == "^/command$"
    assert pattern.tokens[1].arg_name == "string_arg"
    assert pattern.tokens[2].arg_name == "mention"
    assert pattern.tokens[3].arg_name == "hashtag"
    assert pattern.tokens[4].arg_name == "cashtag"

    v4_message = build_v4_message(
        content="/command my_argument <div><span class=\"entity\" data-entity-id=\"0\">@jane-doe</span></div>"
                "<div><span class=\"entity\" data-entity-id=\"1\">#myhashtag</span></div>"
                "<div><span class=\"entity\" data-entity-id=\"2\">$mycashtag</span></div>",
        data="{\"0\":{\"id\":[{\"type\":\"com.symphony.user.userId\",\"value\":\"12345678\"}],"
             "\"type\":\"com.symphony.user.mention\"},"
             "\"1\":{\"id\":[{\"type\":\"org.symphonyoss.taxonomy.hashtag\",\"value\":\"hashtag\"}],"
             "\"type\":\"org.symphonyoss.taxonomy\"},"
             "\"2\":{\"id\":[{\"type\":\"org.symphonyoss.fin.security.id.ticker\",\"value\":\"cashtag\"}],"
             "\"type\":\"org.symphonyoss.fin.security\"}"
             "}")

    match_result = pattern.get_match_result(v4_message)
    expected_match_result = MatchResult(True, {"string_arg": "my_argument",
                                               "mention": Mention("@jane-doe", 12345678),
                                               "hashtag": Hashtag("#myhashtag", "hashtag"),
                                               "cashtag": Cashtag("$mycashtag", "cashtag")})

    assert expected_match_result == match_result


def test_match_result_hashtag():
    pattern = SlashCommandPattern("{#hashtag}")
    v4_message = build_v4_message(
        content="<span class=\"entity\" data-entity-id=\"0\">#myhashtag</span>",

        data="{\"0\":{\"id\":[{\"type\":\"org.symphonyoss.taxonomy.hashtag\",\"value\":\"hashtag\"}],"
             "\"type\":\"org.symphonyoss.taxonomy\"}}")

    match_result = pattern.get_match_result(v4_message)
    expected_match_result = MatchResult(True, {"hashtag": Hashtag("#myhashtag", "hashtag")})

    assert expected_match_result == match_result


def test_match_result_cashtag():
    pattern = SlashCommandPattern("{$cashtag}")
    v4_message = build_v4_message(
        content="<span class=\"entity\" data-entity-id=\"0\">$mycashtag</span>",

        data="{\"0\":{\"id\":[{\"type\":\"org.symphonyoss.fin.security.id.ticker\",\"value\":\"cashtag\"}],"
             "\"type\":\"org.symphonyoss.fin.security\"}}")

    match_result = pattern.get_match_result(v4_message)
    expected_match_result = MatchResult(True, {"cashtag": Cashtag("$mycashtag", "cashtag")})

    assert expected_match_result == match_result


def test_match_result_mention_hashtag_cashtag():
    pattern = SlashCommandPattern("/command {@mention} {#hashtag} {$cashtag}")
    v4_message = build_v4_message(
        content="<div>/command <div><span class=\"entity\" data-entity-id=\"0\">@jane-doe</span></div>"
                "<div><span class=\"entity\" data-entity-id=\"1\">#myhashtag</span></div>"
                "<div><span class=\"entity\" data-entity-id=\"2\">$mycashtag</span></div></div>",
        data="{\"0\":{\"id\":[{\"type\":\"com.symphony.user.userId\",\"value\":\"12345678\"}],"
             "\"type\":\"com.symphony.user.mention\"},"
             "\"1\":{\"id\":[{\"type\":\"org.symphonyoss.taxonomy.hashtag\",\"value\":\"hashtag\"}],"
             "\"type\":\"org.symphonyoss.taxonomy\"},"
             "\"2\":{\"id\":[{\"type\":\"org.symphonyoss.fin.security.id.ticker\",\"value\":\"cashtag\"}],"
             "\"type\":\"org.symphonyoss.fin.security\"}"
             "}")

    match_result = pattern.get_match_result(v4_message)
    expected_match_result = MatchResult(True, {"mention": Mention("@jane-doe", 12345678),
                                               "hashtag": Hashtag("#myhashtag", "hashtag"),
                                               "cashtag": Cashtag("$mycashtag", "cashtag")})

    assert expected_match_result == match_result


def test_match_result_one_static_token_one_argument():
    pattern = SlashCommandPattern("/command {string_arg}")
    v4_message = build_v4_message("<div>/command command2</div>")

    match_result = pattern.get_match_result(v4_message)
    expected_match_result = MatchResult(True, {"string_arg": "command2"})

    assert match_result.is_matching
    assert expected_match_result == match_result


def test_one_mention_not_matching_string_pattern():
    pattern = SlashCommandPattern("{argument_not_mention}")
    v4_message = build_v4_message(
        content="<span class=\"entity\" data-entity-id=\"0\">@jane-doe</span>",
        data="{\"0\":{\"id\":[{\"type\":\"com.symphony.user.userId\",\"value\":\"12345678\"}],"
             "\"type\":\"com.symphony.user.mention\"}}")

    match_result = pattern.get_match_result(v4_message)
    assert not match_result.is_matching
    assert match_result.arguments is None


def test_one_string_argument_not_matching_mention():
    pattern = SlashCommandPattern("{@mention_not_string_argument}")
    v4_message = build_v4_message("@this_is_a_string_not_a_mention")

    match_result = pattern.get_match_result(v4_message)
    assert not match_result.is_matching
    assert match_result.arguments is None


def test_one_hashtag_not_matching_string_pattern():
    pattern = SlashCommandPattern("{argument_not_hashtag}")
    v4_message = build_v4_message(
        content="<span class=\"entity\" data-entity-id=\"0\">#hash_tag_not_string</span>",
        data="{\"0\":{\"id\":[{\"type\":\"org.symphonyoss.taxonomy.hashtag\",\"value\":\"hashtag\"}],"
             "\"type\":\"org.symphonyoss.taxonomy\"}}")

    match_result = pattern.get_match_result(v4_message)
    assert not match_result.is_matching
    assert match_result.arguments is None


def test_one_string_argument_not_matching_hashtag():
    pattern = SlashCommandPattern("{#hashtag_not_string_argument}")
    v4_message = build_v4_message("#this_is_a_string_not_a_hashtag")

    match_result = pattern.get_match_result(v4_message)
    assert not match_result.is_matching
    assert match_result.arguments is None


def test_one_cashtag_not_matching_string_pattern():
    pattern = SlashCommandPattern("{argument_not_hashtag}")
    v4_message = build_v4_message(
        content="<span class=\"entity\" data-entity-id=\"0\">$cash_tag_not_string</span>",
        data="{\"0\":{\"id\":[{\"type\":\"org.symphonyoss.fin.security.id.ticker\",\"value\":\"cashtag\"}],"
             "\"type\":\"org.symphonyoss.fin.security\"}}")

    match_result = pattern.get_match_result(v4_message)
    assert not match_result.is_matching
    assert match_result.arguments is None


def test_one_string_argument_not_matching_cashtag():
    pattern = SlashCommandPattern("{$hashtag_not_string_argument}")
    v4_message = build_v4_message("$this_is_a_string_not_a_cashtag")

    match_result = pattern.get_match_result(v4_message)
    assert not match_result.is_matching
    assert match_result.arguments is None
