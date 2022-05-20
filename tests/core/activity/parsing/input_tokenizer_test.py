from symphony.bdk.core.activity.parsing.message_entities import Cashtag, Hashtag, Mention
from symphony.bdk.core.activity.parsing.input_tokenizer import InputTokenizer
from symphony.bdk.gen.agent_model.v4_message import V4Message


def test_empty_content():
    under_test = build_tokenizer("")
    assert under_test.tokens == []


def test_one_word():
    under_test = build_tokenizer("Hello")
    assert under_test.tokens == ["Hello"]


def test_one_word_with_spaces():
    under_test = build_tokenizer("Hello  ")
    assert under_test.tokens == ["Hello"]


def test_two_words_with_spaces():
    under_test = build_tokenizer("<p>lorem <span>jane-doe</span></p>")
    assert under_test.tokens == ["lorem", "jane-doe"]


# TODO: fix this test
def texst_words_inside_tags():
    under_test = build_tokenizer("ttt<p> edc rtf</p>ddd")
    assert under_test.tokens == ["ttt", "", "edc rtf"]


def test_one_mention():
    under_test = build_tokenizer_with_data(
        "<span class=\"entity\" data-entity-id=\"0\">@jane-doe</span>",
        "{\"0\":{\"id\":[{\"type\":\"com.symphony.user.userId\",\"value\":\"12345678\"}],"
        "\"type\":\"com.symphony.user.mention\"}}")

    assert under_test.tokens == [Mention("@jane-doe", 12345678)]
    assert under_test.tokens[0].user_display_name == "jane-doe"


def test_mention_without_data():
    under_test = build_tokenizer("<span class=\"entity\" data-entity-id=\"0\">@jane-doe</span>")
    assert under_test.tokens == ["@jane-doe"], \
        "The mentions is handled as a string argument since no json entity provided"


def test_two_mentions_with_space():
    under_test = build_tokenizer_with_data(
        "<div><span class=\"entity\" data-entity-id=\"0\">@jane-doe</span> "
        "<span class=\"entity\" data-entity-id=\"1\">@John Doe</span></div>",
        "{\"0\":{\"id\":[{\"type\":\"com.symphony.user.userId\",\"value\":\"12345678\"}],"
        "\"type\":\"com.symphony.user.mention\"},\"1\":{\"id\":[{\"type\":\"com.symphony.user.userId\","
        "\"value\":\"12345679\"}],\"type\":\"com.symphony.user.mention\"}}")

    assert under_test.tokens == [Mention("@jane-doe", 12345678), Mention("@John Doe", 12345679)]
    assert under_test.tokens[0].user_display_name == "jane-doe"
    assert under_test.tokens[1].user_display_name == "John Doe"


def test_two_mentions_without_space():
    under_test = build_tokenizer_with_data(
        "<div><span class=\"entity\" data-entity-id=\"0\">@jane-doe</span>"
        "<span class=\"entity\" data-entity-id=\"1\">@John Doe</span></div>",
        "{\"0\":{\"id\":[{\"type\":\"com.symphony.user.userId\",\"value\":\"12345678\"}],"
        "\"type\":\"com.symphony.user.mention\"},\"1\":{\"id\":[{\"type\":\"com.symphony.user.userId\","
        "\"value\":\"12345679\"}],\"type\":\"com.symphony.user.mention\"}}")

    assert under_test.tokens == [Mention("@jane-doe", 12345678), Mention("@John Doe", 12345679)]
    assert under_test.tokens[0].user_display_name == "jane-doe"
    assert under_test.tokens[1].user_display_name == "John Doe"


def test_text_and_one_mention():
    under_test = build_tokenizer_with_data(
        "<div>lorem<span class=\"entity\" data-entity-id=\"0\">@jane-doe</span></div>",
        "{\"0\":{\"id\":[{\"type\":\"com.symphony.user.userId\",\"value\":\"12345678\"}],"
        "\"type\":\"com.symphony.user.mention\"}}")

    assert under_test.tokens == ["lorem", Mention("@jane-doe", 12345678)]
    assert under_test.tokens[1].user_display_name == "jane-doe"


def test_text_and_two_mentions():
    under_test = build_tokenizer_with_data(
        "<div>lorem<span class=\"entity\" data-entity-id=\"0\">@jane-doe</span>"
        "<span class=\"entity\" data-entity-id=\"1\">@jane-doe-two</span></div>",
        "{\"0\":{\"id\":[{\"type\":\"com.symphony.user.userId\",\"value\":\"12345678\"}],"
        "\"type\":\"com.symphony.user.mention\"},"
        "\"1\":{\"id\":[{\"type\":\"com.symphony.user.userId\",\"value\":\"12345679\"}],"
        "\"type\":\"com.symphony.user.mention\"}}")

    assert under_test.tokens == ["lorem", Mention("@jane-doe", 12345678), Mention("@jane-doe-two", 12345679)]
    assert under_test.tokens[1].user_display_name == "jane-doe"
    assert under_test.tokens[2].user_display_name == "jane-doe-two"


def test_one_hashtag():
    under_test = build_tokenizer_with_data(
        "<div><span class=\"entity\" data-entity-id=\"0\">#myhashtag</span></div>",
        "{\"0\":{\"id\":[{\"type\":\"org.symphonyoss.taxonomy.hashtag\",\"value\":\"hashtag\"}],"
        "\"type\":\"org.symphonyoss.taxonomy\"}}")

    assert under_test.tokens == [Hashtag("#myhashtag", "hashtag")]


def test_words_and_hashtag():
    under_test = build_tokenizer_with_data(
        "<div>mytext1<span class=\"entity\" data-entity-id=\"0\">#myhashtag</span> mytext2</div>",
        "{\"0\":{\"id\":[{\"type\":\"org.symphonyoss.taxonomy.hashtag\",\"value\":\"hashtag\"}],"
        "\"type\":\"org.symphonyoss.taxonomy\"}}")

    assert under_test.tokens == ["mytext1", Hashtag("#myhashtag", "hashtag"), "mytext2"]


def test_words_and_hashtag_with_paragraph():
    under_test = build_tokenizer_with_data(
        "<div>mytext1<span class=\"entity\" data-entity-id=\"0\">#myhashtag</span> <p>mytext2</p></div>",
        "{\"0\":{\"id\":[{\"type\":\"org.symphonyoss.taxonomy.hashtag\",\"value\":\"hashtag\"}],"
        "\"type\":\"org.symphonyoss.taxonomy\"}}")

    assert under_test.tokens == ["mytext1", Hashtag("#myhashtag", "hashtag"), "mytext2"]


def test_one_cashtag():
    under_test = build_tokenizer_with_data(
        "<span class=\"entity\" data-entity-id=\"0\">$mycashtag</span>",
        "{\"0\":{\"id\":[{\"type\":\"org.symphonyoss.fin.security.id.ticker\",\"value\":\"mycashtag\"}],"
        "\"type\":\"org.symphonyoss.fin.security\"}}")

    assert under_test.tokens == [Cashtag("$mycashtag", "mycashtag")]


def build_tokenizer(content):
    return build_tokenizer_with_data(content, "{}")


def build_tokenizer_with_data(content, data):
    return InputTokenizer(build_v4_message(content, data))


def build_v4_message(content, data="{}"):
    return V4Message(
        message="<div data-format=\"PresentationML\" data-version=\"2.0\" class=\"wysiwyg\"><p>" + content +
                "</p></div>",
        data=data)
