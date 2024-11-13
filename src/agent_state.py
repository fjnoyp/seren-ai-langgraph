from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

# https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.message.add_messages

# State keys without an annotation will be overwritten by each update, storing the most recent value. 

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    ui_context: Annotated[str, ""]
