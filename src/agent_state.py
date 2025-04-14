from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from enum import Enum


# https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.message.add_messages

# State keys without an annotation will be overwritten by each update, storing the most recent value.


class AiBehaviorMode(Enum):
    CHAT = "chat"
    SINGLE_CALL = "single_call"
    FILE_PROCESSOR = "file_processor"


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

    # Single or chat mode behavior
    ai_behavior_mode: Optional[str] = None

    # Context of the UI, for example the current page or view
    ui_context: Optional[str] = None

    # Plan of what's been done and everything that still needs to be done
    plan: Optional[str] = None

    # Feedback from previous node
    prev_node_feedback: Optional[str] = None

    # Iteration count
    iteration_count: Optional[int] = None

    # Next Node to go to
    next_node: Optional[str] = None
