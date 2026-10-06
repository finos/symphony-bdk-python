"""Service exposing emoji reactions on messages.

Reactions are a Symphony Messaging feature that users rely on, but they are not
described in the published Agent or Pod API specification, so no generated
client covers them. This service calls the same pod endpoint the Symphony
clients use, following the precedent set by
:class:`symphony.bdk.core.service.message.multi_attachments_messages_api.MultiAttachmentsMessagesApi`
for endpoints the generated code does not reach.
"""

import base64
import binascii
import json
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig
from symphony.bdk.core.retry import retry
from symphony.bdk.gen.api_client import ApiClient

REACTIONS_PATH = "/maestro/reactions/v1/message"


def to_padded_base64(message_id: str) -> str:
    """Convert a message id to the padded, non URL-safe form reactions match on.

    Message ids are handed out URL-safe and unpadded elsewhere in the API, but
    the reactions endpoint matches on the standard alphabet with padding. Ids
    that are already in that form are returned unchanged.

    :param message_id: A message id in either encoding.
    :return: The message id in padded standard base64.
    """
    converted = message_id.replace("-", "+").replace("_", "/")
    padded = converted + "=" * (-len(converted) % 4)
    try:
        base64.b64decode(padded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"{message_id!r} is not a base64 message id") from exc
    return padded


class ReactionService:
    """Service class for adding, removing and listing emoji reactions on messages.

    Reactions may be disabled for a pod, or restricted in external and federated
    rooms, in which case these calls fail with the pod's own error.
    """

    def __init__(
        self, pod_client: ApiClient, auth_session: AuthSession, retry_config: BdkRetryConfig
    ):
        self._pod_client = pod_client
        self._auth_session = auth_session
        self._retry_config = retry_config

    async def _call(
        self, method: str, path: str, body: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        headers = {
            "Accept": "application/json",
            "sessionToken": await self._auth_session.session_token,
        }
        if body is not None:
            headers["Content-Type"] = "application/json"

        response = await self._pod_client.call_api(
            method,
            self._pod_client.configuration.host + path,
            header_params=headers,
            body=json.dumps(body) if body is not None else None,
        )
        data = getattr(response, "data", None)
        if not data:
            return None
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        try:
            return json.loads(data)
        except ValueError:
            return None

    @retry
    async def react(self, message_id: str, emoji: str) -> None:
        """Add a reaction to a message on behalf of the calling user.

        Reacting twice with the same emoji leaves a single reaction.

        :param message_id: Id of the message to react to.
        :param emoji: The emoji character itself, such as ``"\\N{THUMBS UP SIGN}"``.
            Shortnames such as ``"thumbsup"`` are rejected by the pod.
        """
        if not emoji or not emoji.strip():
            raise ValueError("emoji is required; the pod rejects an empty reaction")
        await self._call(
            "POST",
            REACTIONS_PATH,
            {
                "messageId": to_padded_base64(message_id),
                "emoji": emoji,
                "timestamp": int(time.time() * 1000),
            },
        )

    @retry
    async def unreact(self, message_id: str) -> None:
        """Remove the calling user's reaction from a message.

        The emoji is deliberately omitted: the pod rejects an empty string, and
        reacting again with the same emoji is a no-op rather than a toggle, so
        leaving the field out is what clears the reaction.

        :param message_id: Id of the message to clear the reaction from.
        """
        await self._call(
            "POST",
            REACTIONS_PATH,
            {
                "messageId": to_padded_base64(message_id),
                "timestamp": int(time.time() * 1000),
            },
        )

    @retry
    async def list_reactions(self, message_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """List the reactions on a message, keyed by emoji.

        :param message_id: Id of the message. For an edited message this is the
            id of the original, which is what the reactions are attached to.
        :return: A mapping of emoji to the reactions on it, each carrying the
            reacting ``userId`` and a timestamp. Empty when there are none.
        """
        encoded = quote(to_padded_base64(message_id), safe="")
        payload = await self._call("GET", f"{REACTIONS_PATH}?initialMessageId={encoded}")
        if not isinstance(payload, dict):
            return {}
        reactions = payload.get("reactions")
        return reactions if isinstance(reactions, dict) else {}
