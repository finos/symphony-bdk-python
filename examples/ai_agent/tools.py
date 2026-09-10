"""BDK-backed tools exposed to the LLM agent."""

from langchain_core.tools import tool

from examples.ai_agent.memory_ids import stream_id_from_thread
from symphony.bdk.core.symphony_bdk import SymphonyBdk


def build_tools(bdk: SymphonyBdk):
    @tool
    async def lookup_user(username_or_email: str) -> str:
        """Look up a Symphony user by username or email address and return their profile."""
        if "@" in username_or_email:
            result = await bdk.users().list_users_by_emails([username_or_email])
        else:
            result = await bdk.users().list_users_by_usernames([username_or_email])

        if not result.users:
            return f"No user found for '{username_or_email}'."

        user = result.users[0]
        return (
            f"id={user.id}, username={user.username}, display_name={user.display_name}, "
            f"email={user.email_address}"
        )

    @tool
    async def list_current_room_members(thread_id: str) -> str:
        """List the members of the room/IM the conversation identified by thread_id is happening in."""
        stream_id = stream_id_from_thread(thread_id)
        members = await bdk.streams().list_room_members(stream_id)
        member_ids = [str(member.id) for member in members.value]
        return f"Room members (user ids): {', '.join(member_ids)}"

    @tool
    async def send_message_to_stream(stream_id: str, message: str) -> str:
        """Send a message to an arbitrary Symphony stream identified by stream_id."""
        await bdk.messages().send_message(stream_id, f"<messageML>{message}</messageML>")
        return f"Message sent to stream {stream_id}."

    return [lookup_user, list_current_room_members, send_message_to_stream]
