## Why

The Java BDK ships `bdk-ai-agent-example`, showing how little code turns a bot into an LLM-backed
agent with BDK tools. Python BDK has no equivalent, and it's a common ask ("how do I plug an LLM
into my bot"). Adding one closes that gap and gives users a runnable reference.

## What Changes

- New standalone example `examples/ai_agent/` mirroring the Java example's shape but idiomatic to
  the Python BDK (async, `CommandActivity` instead of `PatternCommandActivity`, LangGraph instead
  of LangChain4j `AiServices`).
- A `ChatVertexAI` (Gemini) model wired into a LangGraph ReAct-style agent (`create_react_agent`)
  exposing BDK-backed tools: look up a user, list current room members, send a message to a
  stream.
- Conversation memory keyed per `(stream_id, user_id)` via LangGraph's checkpointer `thread_id`,
  mirroring the Java `MemoryIds` helper.
- A `CommandActivity` subclass matching any message addressed to the bot (`@BotMention <question>`)
  that forwards the text to the agent and replies with its answer.
- README documenting setup (`~/.symphony/config.yaml`, GCP ADC auth, env vars, extra pip installs)
  since this example needs third-party packages not in the BDK's own dependencies.

## Capabilities

### New Capabilities
- `ai-agent-example`: an `examples/` module demonstrating an LLM agent (LangGraph + Vertex AI
  Gemini) wired to Symphony via BDK activities, tools, and per-conversation memory.

### Modified Capabilities
(none — no changes to existing spec-level BDK behavior)

## Impact

- Adds a new directory under `examples/` only; no changes to `symphony/bdk/*` production code.
- New third-party runtime dependencies for this example only (`langgraph`,
  `langchain-google-vertexai`), documented in the example's own README, not added to the core
  `pyproject.toml` (no existing precedent for per-example deps in this repo, per `pyproject.toml`
  dependency review — extra libs will be called out with a `pip install` line instead).
