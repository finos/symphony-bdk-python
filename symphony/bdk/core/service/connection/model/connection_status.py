import enum


class ConnectionStatus(enum.Enum):
    """The list of all possible values for the request listing connection status.
    See: `List Connections <https://developers.symphony.com/restapi/reference#list-connections>`_
    """
    ALL = "ALL"
    PENDING_INCOMING = "PENDING_INCOMING"
    PENDING_OUTGOING = "PENDING_OUTGOING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
