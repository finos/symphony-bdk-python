"""This module contains a set of util functions providing stream id conversion.
It is possible to make conversion from the original stream id to the URLSafe encoded stream id and viceversa.
"""
import base64


def to_url_safe_stream_id(stream_id: str) -> str:
    """Convert the stream id to the corresponding URLSafe encoded stream id

    :param stream_id: stream id of the stream to be parsed
    :return: stream id after conversion
    """
    decoded_url_bytes = base64.b64decode(stream_id)
    url_safe_encoded_str = base64.urlsafe_b64encode(decoded_url_bytes)
    return str(url_safe_encoded_str, "utf-8").rstrip("=")


def from_url_safe_stream_id(stream_id: str) -> str:
    """Convert the URLSafe encoded stream id to the corresponding original stream id

    :param stream_id: streamId of the stream to be parsed
    :return: stream id after conversion
    """
    decoded_url_bytes = base64.urlsafe_b64decode(stream_id + "==")
    encoded_str = base64.b64encode(decoded_url_bytes)
    return str(encoded_str, "utf-8")
