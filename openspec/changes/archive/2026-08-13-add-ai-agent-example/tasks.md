## 1. Scaffolding

- [x] 1.1 Create `examples/ai_agent/` directory
- [x] 1.2 Add `examples/ai_agent/__init__.py` (empty, matches other example folders' layout)

## 2. Memory keying

- [x] 2.1 Add `examples/ai_agent/memory_ids.py` with a `thread_id(stream_id, user_id)` helper
  building `f"{stream_id}::{user_id}"`, and a `stream_id_from_thread(thread_id)` reverse helper for
  tool calls that need the current stream

## 3. BDK tools

- [x] 3.1 Add `examples/ai_agent/tools.py` with a `build_tools(bdk)` function returning a list of
  `@tool`-decorated async callables closing over the `SymphonyBdk` instance:
  - `lookup_user(username_or_email)` using `bdk.users().list_users_by_usernames(...)` or
    `list_users_by_emails(...)` depending on whether the input contains `@`
  - `list_current_room_members(thread_id)` using `bdk.streams().list_room_members(...)`, resolving
    the stream id from `thread_id` via `memory_ids.stream_id_from_thread`
  - `send_message_to_stream(stream_id, message)` using `bdk.messages().send_message(...)`,
    wrapping `message` in `<messageML>`

## 4. Agent wiring

- [x] 4.1 Add `examples/ai_agent/agent.py` with a `build_agent(bdk)` function that constructs a
  `ChatVertexAI` model (reading `GCP_PROJECT_ID`/`GCP_LOCATION`/`GEMINI_MODEL_NAME` env vars, with
  defaults matching the Java example) and returns a LangGraph `create_react_agent` wired with
  `build_tools(bdk)` and a `MemorySaver` checkpointer
- [x] 4.2 Include a system prompt instructing the agent to answer concisely (rendered as a chat
  message) and describing the available tools, mirroring the Java `Assistant` interface's
  `@SystemMessage`

## 5. Activity

- [x] 5.1 Add `examples/ai_agent/ask_ai_activity.py` with an `AskAiActivity(CommandActivity)`
  subclass:
  - `matches(context)` returns true when `context.text_content` starts with
    `@{context.bot_display_name}` followed by a non-empty question
  - `on_activity(context)` strips the bot mention, builds the `thread_id` from
    `context.stream_id` and the initiator's user id, invokes the agent, and sends the reply via
    `messages().send_message(...)`

## 6. Entry point

- [x] 6.1 Add `examples/ai_agent/main.py`: loads config from `~/.symphony/config.yaml` via
  `BdkConfigLoader`, constructs `SymphonyBdk`, builds the agent, registers `AskAiActivity`, and
  starts the datafeed loop — mirroring `examples/activities/` entry-point style

## 7. Documentation

- [x] 7.1 Add `examples/ai_agent/README.md` covering: what the example demonstrates, required
  `pip install langgraph langchain-google-vertexai`, `gcloud auth application-default login`
  prerequisite, required/optional env vars table, how to run, and a short architecture diagram
  (mirroring the Java example's README)

## 8. Verification

- [x] 8.1 Run `poetry run ruff check examples` and `poetry run ruff format --check examples` to
  confirm the new files pass lint/format
- [x] 8.2 Manually smoke-test against a real bot/config: `@BotMention what can you do?` gets a
  reply, a follow-up in the same stream shows memory, a question needing a tool call (user lookup
  or room members) resolves correctly
