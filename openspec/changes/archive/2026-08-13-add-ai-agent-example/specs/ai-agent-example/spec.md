## ADDED Requirements

### Requirement: Bot forwards addressed messages to an LLM agent
The example SHALL register an activity that matches any message addressed to the bot
(`@BotMention <question>`) and forwards the question text to an LLM agent, then sends the agent's
answer back to the originating stream.

#### Scenario: User asks the bot a question
- **WHEN** a user sends `@BotMention what can you do?` in a stream the bot is a member of
- **THEN** the example forwards `what can you do?` to the LLM agent and sends the agent's reply as
  a message back to that stream

### Requirement: LLM agent has BDK-backed tools
The LLM agent SHALL be given tools, implemented on top of BDK services, to look up a Symphony
user, list the members of the current room/IM, and send a message to an arbitrary stream — and
SHALL decide on its own whether and when to invoke them based on the user's question.

#### Scenario: Question requires a user lookup
- **WHEN** the forwarded question asks the agent to find a user (e.g. "what's the email of jdoe?")
- **THEN** the agent invokes the user-lookup tool and includes the result in its answer

#### Scenario: Question requires listing room members
- **WHEN** the forwarded question asks the agent about the members of the current room/IM
- **THEN** the agent invokes the room-members tool, scoped to the stream the question came from

#### Scenario: Question requires sending a message elsewhere
- **WHEN** the forwarded question asks the agent to relay a message to a specific stream id
- **THEN** the agent invokes the send-message tool with that stream id and message content

### Requirement: Conversation memory is scoped per stream and user
The example SHALL maintain separate conversation memory for each distinct `(stream_id, user_id)`
pair, so that the agent recalls prior context only for the same person in the same
room/IM, and does not mix context across different users or streams.

#### Scenario: Same user, same stream, follow-up question
- **WHEN** a user asks a follow-up question in the same stream after a prior exchange
- **THEN** the agent's answer reflects the context of the prior exchange in that stream

#### Scenario: Same user, different stream
- **WHEN** the same user asks a question in a different stream than a prior exchange
- **THEN** the agent treats it as a new conversation, with no memory of the other stream's
  exchange

#### Scenario: Different user, same stream
- **WHEN** a different user asks a question in a stream where another user previously talked to
  the agent
- **THEN** the agent treats it as a new conversation, with no memory of the other user's exchange
