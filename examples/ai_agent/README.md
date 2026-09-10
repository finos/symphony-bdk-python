# AI Agent example

Wires an LLM agent (LangGraph + Vertex AI Gemini) into a Symphony bot: any message addressed to
the bot (`@BotMention <question>`) is forwarded to the agent, which can call BDK-backed tools and
replies in the same stream. Mirrors the Java BDK's `bdk-ai-agent-example`.

## Architecture

```
Symphony message  -->  AskAiActivity (CommandActivity)  -->  LangGraph ReAct agent (Gemini)
                                                                    |
                                                       +------------+------------+
                                                       |            |            |
                                                 lookup_user  list_current   send_message
                                                              _room_members  _to_stream
```

Conversation memory is kept in-memory (LangGraph `MemorySaver`), keyed per `(stream_id, user_id)`
via a `thread_id` built as `f"{stream_id}::{user_id}"` (`memory_ids.py`). Memory does not survive
process restarts.

## Prerequisites

- A working `~/.symphony/config.yaml` bot configuration (see the repo's `examples/authentication`
  for reference).
- Extra dependencies, not part of the BDK's own dependencies:

  ```bash
  pip install langgraph langchain-google-vertexai
  ```

- Google Cloud auth for Vertex AI:

  ```bash
  gcloud auth application-default login
  ```

## Environment variables

| Variable           | Required | Default              | Description                          |
|---------------------|----------|-----------------------|---------------------------------------|
| `GCP_PROJECT_ID`    | yes      | -                      | GCP project used for Vertex AI calls  |
| `GCP_LOCATION`      | no       | `us-central1`          | Vertex AI region                      |
| `GEMINI_MODEL_NAME` | no       | `gemini-1.5-flash`     | Gemini model used by the agent        |

## Running

From the repository root:

```bash
GCP_PROJECT_ID=my-project python -m examples.ai_agent.main
```

## Usage

- `@BotMention what can you do?` — general question, answered directly by the LLM.
- `@BotMention what's the email of jdoe?` — triggers the user-lookup tool.
- `@BotMention who's in this room?` — triggers the room-members tool, scoped to the stream the
  question came from.
- `@BotMention send "hello" to stream <streamId>` — triggers the send-message tool.
- Asking a follow-up question in the same stream reuses conversation memory; the same question
  from a different user, or in a different stream, starts a new conversation.

## Limitations

- Conversation memory is in-memory only (lost on restart), same as the Java example.
- Tested against LangGraph `>=0.2` and `langchain-google-vertexai`'s current API surface at time
  of writing; both libraries evolve quickly and this example is illustrative, not covered by the
  BDK's own compatibility guarantees.
