from examples.ai_agent.memory_ids import thread_id
from symphony.bdk.core.activity.command import CommandActivity, CommandContext
from symphony.bdk.core.service.message.message_service import MessageService


class AskAiActivity(CommandActivity):
    """Forwards any message addressed to the bot to the LLM agent and replies with its answer."""

    def __init__(self, messages: MessageService, agent):
        self._messages = messages
        self._agent = agent
        super().__init__()

    def matches(self, context: CommandContext) -> bool:
        mention = "@" + context.bot_display_name
        text = context.text_content.strip()
        return text.startswith(mention) and text[len(mention) :].strip() != ""

    async def on_activity(self, context: CommandContext):
        mention = "@" + context.bot_display_name
        question = context.text_content.strip()[len(mention) :].strip()

        tid = thread_id(context.stream_id, context.initiator.user.user_id)
        result = await self._agent.ainvoke(
            {"messages": [("user", f"[thread_id={tid}] {question}")]},
            config={"configurable": {"thread_id": tid}},
        )
        answer = result["messages"][-1].content

        await self._messages.send_message(context.stream_id, f"<messageML>{answer}</messageML>")
