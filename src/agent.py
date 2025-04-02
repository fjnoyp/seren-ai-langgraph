from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END

from langgraph.graph import StateGraph

from langchain_core.messages import (
    AIMessage,
    ToolMessage,
)
from langgraph.types import Command, interrupt

from langchain_core.runnables.config import RunnableConfig

from src.agent_state import AgentState, AiBehaviorMode

from src.config_schema import ConfigSchema
from src.tools import tools
from src.tools.tools import get_ai_request_tools, get_all_tools

# Import LLM configurations
from src.llm_config import single_call_llm

# Import the new node implementations
from src.nodes.node_planner import node_planner
from src.nodes.node_response_generator import node_response_generator
from src.nodes.node_tool_caller import node_tool_caller

from langgraph.prebuilt import ToolNode

# === Load Environment Variables (.env) ===
load_dotenv()


graph_builder = StateGraph(AgentState, ConfigSchema)


# === START - route by ai behavior mode (ie. single call or chat)
def edge_route_by_ai_behavior_mode(state: AgentState):
    ai_behavior_mode = state.get("ai_behavior_mode")
    if ai_behavior_mode is None or ai_behavior_mode == "":
        return AiBehaviorMode.CHAT.value
    return ai_behavior_mode


graph_builder.add_conditional_edges(
    START,
    edge_route_by_ai_behavior_mode,
    {"chat": "planner", "single_call": "single_call"},
)


def node_single_call(state: AgentState, config: RunnableConfig):
    response = single_call_llm.invoke(state["messages"])
    return {"messages": [response]}


graph_builder.add_node("single_call", node_single_call)


# === PLANNER - Decide next step
graph_builder.add_node("planner", node_planner)


# Decide next step based on planner decision
def edge_planner_decision(state: AgentState):
    next_node = state.get("next_node")
    if next_node == "tool_caller":
        return "tool_caller"
    elif next_node == "response_generator":
        return "response_generator"
    else:
        raise ValueError(f"Invalid next action: {next_node}")


graph_builder.add_conditional_edges(
    "planner",
    edge_planner_decision,
    {
        "tool_caller": "tool_caller",
        "response_generator": "response_generator",
    },
)

# === RESPONSE GENERATOR
graph_builder.add_node("response_generator", node_response_generator)
graph_builder.add_edge("response_generator", END)

# === TOOL EXECUTOR
graph_builder.add_node("tool_caller", node_tool_caller)


# Add conditional edge for tool_caller to route based on next_node
def edge_tool_caller_decision(state: AgentState):
    next_node = state.get("next_node", "")
    if next_node == "planner":
        return "planner"  # Route to planner on errors
    else:
        return "tools"  # Normal flow to tools


# Conditional edge for tool_caller
graph_builder.add_conditional_edges(
    "tool_caller",
    edge_tool_caller_decision,
    {
        "planner": "planner",  # Route to planner on errors
        "tools": "tools",  # Normal successful flow
    },
)

# def node_tool_executor(state: AgentState, config: RunnableConfig):
#     # Providing context allows tools to be auto called with certain parameter values
#     # user_id = config["configurable"].get("user_id")
#     # org_id = config["configurable"].get("org_id")
#     # Set the tool context with user and org information (UNUSED FOR NOW - as ai makes requests to client directly instead)
#     # with set_tool_context({"timezone": timezone, "language": language}):
#     return ToolNode(get_all_tools()).ainvoke(state)  # , config)

graph_builder.add_node("tools", ToolNode(get_all_tools()))

graph_builder.add_edge("tools", "execute_ai_request_on_client")


# === EXECUTE AI REQUEST ON CLIENT
# Node interrupted - client expected to respond and update tool message with result
def node_execute_ai_request_on_client(state: AgentState):
    # Get the client's response to the AI request
    ai_request_result = interrupt("Provide client ai request execution result:")

    # Get the current messages
    messages = state["messages"]

    if not messages:
        return {
            "messages": [],
            "prev_node_feedback": "Error: No messages found in state to update.",
        }

    # Get the last message (assumed to be a tool message)
    last_message = messages[-1]

    # Create an updated version of the last message with the same ID
    # This will cause add_messages to replace the original
    from langchain_core.messages import ToolMessage

    # Create a new tool message with the same ID and tool_call_id (if present)
    updated_message = ToolMessage(
        content=ai_request_result,
        tool_call_id=getattr(last_message, "tool_call_id", None),
        id=last_message.id if hasattr(last_message, "id") else None,
    )

    # Return updated state
    # The add_messages reducer will handle replacing the old message with the new one
    return {"messages": [updated_message], "prev_node_feedback": ""}


graph_builder.add_node(
    "execute_ai_request_on_client", node_execute_ai_request_on_client
)


graph_builder.add_edge("execute_ai_request_on_client", "planner")

# === Compile Graph ===
# No memory is needed for cloud
graph = graph_builder.compile(
    # interrupt_before=["execute_ai_request_on_client"],
)
