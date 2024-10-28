from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq


from typing_extensions import TypedDict
from dotenv import load_dotenv

from typing import Annotated, Type

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from pydantic import BaseModel

from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, trim_messages

from langchain_core.messages.tool import ToolCall

from langchain_core.tools import tool
from langchain_core.tools import BaseTool

from langchain_core.runnables.config import RunnableConfig


from pydantic import BaseModel, Field

import task_tools

# MAIN TODO
# 1. Make basic calls to graph from javascript and then flutter code
# 2. make test calls using config object and verify the chat thread histories are different


# === Load Environment Variables (.env) ===
load_dotenv()


# === Graph State ===
# All Graph Nodes must accept this type
# Any inputs to Graph must be of this type


class ConfigSchema(TypedDict):
    user_id: str
    org_id: str


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(AgentState, ConfigSchema)

# ==================
# === TOOLS ===
# ==================

# === TAVILY TOOL ===
tavily = TavilySearchResults(max_results=2)


# === SHIFTS TOOL ===
# Goal: get current shift / clock in or out of current shift / get shift history for specific day / ask questions about shifts?


tools = [
    *task_tools,
    # tavily,
]

graph_builder.add_node("tools", ToolNode(tools))

# Thoughts
# How should tool structuring be done?
# Should ai execute all tools immediately ... if not what should the response from the tools to indicate the status
# Similarly how might we implement user confirmation of task calls?


# === Define LLM ===
# Consider Routing: https://console.groq.com/docs/tool-use#routing-system

# tool-user-preview model overeager tool call
# llm = ChatGroq(model="llama3-groq-8b-8192-tool-use-preview")

# this model is more balanced
# model still fails at basic tasks - calling tools too aggressively
# llm = ChatGroq(model="llama-3.1-8b-instant")

# claude-3-5-sonnet is better, but very expensive
# https://console.anthropic.com/settings/billing
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

llm_with_tools = llm.bind_tools(tools)


def chatbot(state: AgentState, config: RunnableConfig):

    # Check the config object
    print("Config:")

    user_id = config["configurable"].get("user_id")
    org_id = config["configurable"].get("org_id")

    # Return config variables to check they are received
    # return {"messages" : AIMessage(content= "user_id: " + user_id + " org_id: " + org_id)}

    messages = trim_messages(
        state["messages"],
        # only use last 3 messages
        strategy="last",
        token_counter=len,
        max_tokens=3,
        # Most chat models expect that chat history starts with either:
        # (1) a HumanMessage or
        # (2) a SystemMessage followed by a HumanMessage
        start_on="human",
        # Most chat models expect that chat history ends with either:
        # (1) a HumanMessage or
        # (2) a ToolMessage
        end_on=("human", "tool"),
        # Usually, we want to keep the SystemMessage
        # if it's present in the original history.
        # The SystemMessage has special instructions for the model.
        include_system=True,
    )

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


graph_builder.add_node("chatbot", chatbot)


def select_next_node(state: AgentState):
    return tools_condition(state)


graph_builder.add_conditional_edges(
    "chatbot", select_next_node, {"tools": "tools", END: END}
)


# TODO work on tool execution conditional branching
def tool_execution(state: AgentState):
    return END


graph_builder.add_conditional_edges("tools", tool_execution, {END: END})

# graph_builder.set_entry_point("chatbot")
graph_builder.add_edge(START, "chatbot")

graph_builder.add_edge("chatbot", END)

# === Compile Graph ===
# No memory is needed for cloud
graph = graph_builder.compile()
