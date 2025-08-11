from symphony.bdk.core.service.message.messageml_util import escape_special_chars


def test_escape_special_chars_match_found():
    text = "\\.hello"
    expected_text = "&#92;&#46;hello"
    assert expected_text == escape_special_chars(text)


def test_escape_special_chars_no_match_found():
    text = "hello."
    expected_text = "hello&#46;"
    assert expected_text == escape_special_chars(text)


def test_escape_special_chars_multiple_matches():
    text = "Here's multiple chars <'\"$#=.[]"
    expected_text = (
        "Here&apos;s multiple chars &lt;&apos;&quot;&#36;&#35;&#61;&#46;&#91;&#93;"
    )
    assert expected_text == escape_special_chars(text)


def test_escape_special_chars_no_change():
    text = "  This text will remain the same  "
    assert text == escape_special_chars(text)
