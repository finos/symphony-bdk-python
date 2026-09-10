"""Wires a LangGraph ReAct agent, backed by Vertex AI Gemini, with BDK tools and per-conversation memory."""

import os

from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from examples.ai_agent.tools import build_tools
from symphony.bdk.core.symphony_bdk import SymphonyBdk

SYSTEM_PROMPT = (
    "You are a helpful assistant embedded in a Symphony chat bot. Answer concisely.\n"
    "You have access to tools to look up a Symphony user by username or email, list the "
    "members of the current room/IM, and send a message to an arbitrary stream.\n"
    "Messages you receive are prefixed with '[thread_id=<id>]': use that thread_id verbatim "
    "when calling the room-members tool, and never repeat it in your answer."
)


def build_agent(bdk: SymphonyBdk):
    model = ChatVertexAI(
        model_name=os.environ.get("GEMINI_MODEL_NAME", "gemini-1.5-flash"),
        project=os.environ["GCP_PROJECT_ID"],
        location=os.environ.get("GCP_LOCATION", "us-central1"),
    )
    return create_react_agent(
        model,
        tools=build_tools(bdk),
        prompt=SYSTEM_PROMPT,
        checkpointer=MemorySaver(),
    )
