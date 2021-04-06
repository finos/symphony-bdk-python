"""This module handles pre-processing for an outgoing message in order to have a valid messageML format.
"""
import re


def escape_special_chars(raw_text: str) -> str:
    """ Replace all special characters placed within the messageML that must be HTML-escaped
    to have a valid MessageML format.

    :param raw_text: text to be parsed
    :return: text in a valid messageML format
    """
    current_parsed_index = 0
    parsed_text = ""
    matches = re.finditer(_pattern(), raw_text)
    for match in matches:
        parsed_text += raw_text[current_parsed_index:match.start()] + _replacement(match.group(0))
        current_parsed_index = match.end()
    return parsed_text + raw_text[current_parsed_index:]


def _pattern():
    return "|".join(_special_chars_dict)


def _replacement(match):
    return _special_chars_dict.get(match, _special_chars_dict.get("\\" + match))


_special_chars_dict = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&apos;",
    "\"": "&quot;",
    "#": "&#35;",
    "\\$": "&#36;",
    "%": "&#37;",
    "\\(": "&#40;",
    "\\)": "&#41;",
    "\\*": "&#42;",
    "\\.": "&#46;",
    ";": "&#59;",
    "=": "&#61;",
    "\\[": "&#91;",
    "\\\\": "&#92;",
    "\\]": "&#93;",
    "`": "&#96;",
    "\\{": "&#123;",
    "\\}": "&#125;"
}
