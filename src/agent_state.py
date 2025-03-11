from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from enum import Enum


# https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.message.add_messages

# State keys without an annotation will be overwritten by each update, storing the most recent value.


class AiBehaviorMode(Enum):
    CHAT = "chat"
    SINGLE_CALL = "single_call"


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    ui_context: str
    ai_behavior_mode: str
    plan: str
