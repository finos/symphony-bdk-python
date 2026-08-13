## Context

Reference: [symphony-bdk-java `bdk-ai-agent-example`](https://github.com/finos/symphony-bdk-java/tree/main/symphony-bdk-examples/bdk-ai-agent-example).
It wires LangChain4j `AiServices` (a typed `Assistant` interface implemented at runtime) to a
Vertex AI Gemini chat model, gives it BDK-backed `@Tool` methods, and keys per-conversation memory
by `(streamId, userId)`. A `PatternCommandActivity` forwards any `@bot <question>` message to the
assistant and posts the answer back.

Python BDK (`symphony/bdk/core/`) has no `PatternCommandActivity` or `AiServices`-equivalent, and
is fully async (`asyncio`). The example must be built from Python-idiomatic primitives:
`CommandActivity` (`symphony/bdk/core/activity/command.py`) for message dispatch, and an
agent/tool framework with native async + tool-calling support.

## Goals / Non-Goals

**Goals:**
- One runnable example under `examples/ai_agent/` closely mirroring the Java example's structure
  and behavior (same 3 tools, same memory-keying scheme, same `@bot <question>` UX).
- Idiomatic async Python throughout — no blocking calls inside the datafeed loop.
- Self-contained: extra dependencies isolated to the example, not the core package.

**Non-Goals:**
- No new production code in `symphony/bdk/core` or `symphony/bdk/gen`.
- Not tied to Vertex AI specifically — the model choice is illustrative, swappable.
- No persistence of conversation memory across process restarts (in-memory only, same as Java).

## Decisions

- **Agent framework: LangGraph (`create_react_agent`) over LangChain4j-style `AiServices`.**
  Python LangChain's closest analogue to `AiServices`'s implicit tool-calling loop is LangGraph's
  prebuilt `create_react_agent`, which takes a chat model + a list of tools and runs the
  reason/act loop for you — no hand-rolled agent loop needed. Plain LangChain `AgentExecutor` was
  considered but is legacy/deprecated in favor of LangGraph as of LangChain's own docs.
- **Model: `langchain-google-vertexai`'s `ChatVertexAI` (Gemini) over other providers.**
  Matches the Java example 1:1 (same Vertex AI Gemini backend, same env vars: `GCP_PROJECT_ID`,
  `GCP_LOCATION`, model name), so setup instructions and auth (`gcloud auth application-default
  login`) carry over directly.
- **Memory: LangGraph checkpointer (`MemorySaver`) keyed by `thread_id` over a custom memory map.**
  LangGraph's `create_react_agent` already accepts a `checkpointer` and threads state by a
  `thread_id` config key — this is a drop-in replacement for the Java example's hand-rolled
  `MessageWindowChatMemory` + `MemoryIds` helper. `thread_id` is built the same way as Java's
  `MemoryIds.of(streamId, userId)`: `f"{stream_id}::{user_id}"`.
- **Activity: custom `CommandActivity` subclass over a new `PatternCommandActivity` base class.**
  Python BDK has no regex-pattern activity base class, and adding one to core would be a
  production-code change out of scope for an example. Instead, `AskAiActivity` subclasses
  `CommandActivity` directly and does the `@bot <question>` matching itself in `matches()`,
  consistent with `examples/activities/command_activity.py`'s existing pattern.
- **Tools as async functions wrapped with `@tool` over sync wrappers.**
  All BDK service calls are `async def`; LangChain's `@tool` decorator supports async tool
  functions natively, so tools call `await self._bdk.users().list_users_by_usernames(...)` etc.
  directly without threads or sync bridging.
- **Dependencies stay out of `pyproject.toml`.**
  No existing example depends on a non-BDK third-party package, and `pyproject.toml` has no
  `[tool.poetry.extras]` mechanism. Adding `langgraph`/`langchain-google-vertexai` as core deps
  would bloat every BDK install for one example. Instead, the example's own README documents
  `pip install langgraph langchain-google-vertexai`.

## Risks / Trade-offs

- [LangGraph/LangChain API surface changes fast] → Pin example instructions to tested versions in
  the README; example is illustrative, not covered by BDK's own compatibility guarantees.
- [In-memory-only conversation memory] → Same limitation as the Java example; acceptable for a
  demo, call it out explicitly in the README.
- [GCP/Vertex AI dependency makes the example non-runnable without cloud credentials] → Matches
  Java example's own trade-off; document `gcloud auth application-default login` prerequisite
  clearly, same as Java's README.

## Open Questions

None — scope is a self-contained example, no ambiguity requiring a decision from the user.
