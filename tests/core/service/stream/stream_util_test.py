from symphony.bdk.core.service.stream.stream_util import to_url_safe_stream_id, from_url_safe_stream_id


def test_to_url_safe_stream_id():
    stream_id = "XlU3OH9eVMzq+yss7M/xyn///oxwgbtGbQ=="
    url_safe_stream_id = to_url_safe_stream_id(stream_id)
    assert url_safe_stream_id == "XlU3OH9eVMzq-yss7M_xyn___oxwgbtGbQ"


def test_from_url_safe_stream_id():
    url_safe_stream_id = "XlU3OH9eVMzq-yss7M_xyn___oxwgbtGbQ"
    stream_id = from_url_safe_stream_id(url_safe_stream_id)
    assert stream_id == "XlU3OH9eVMzq+yss7M/xyn///oxwgbtGbQ=="
