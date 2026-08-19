"""Builds/parses the LangGraph checkpointer thread_id from a (stream_id, user_id) pair."""

_SEPARATOR = "::"


def thread_id(stream_id: str, user_id: int) -> str:
    return f"{stream_id}{_SEPARATOR}{user_id}"


def stream_id_from_thread(thread_id: str) -> str:
    return thread_id.split(_SEPARATOR, 1)[0]
