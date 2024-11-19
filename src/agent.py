from contextlib import contextmanager
from contextvars import ContextVar
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq


from typing_extensions import TypedDict
from dotenv import load_dotenv

from typing import Annotated, Type

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from typing import Annotated


from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from pydantic import BaseModel

from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    ToolMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
)

from langchain_core.messages.tool import ToolCall

from langchain_core.tools import tool
from langchain_core.tools import BaseTool

from langchain_core.runnables.config import RunnableConfig


from pydantic import BaseModel, Field

from src.agent_state import AgentState

from src.config_schema import ConfigSchema
from src.tools.tool_node import get_ai_request_tools, tool_node, get_all_tools

from functools import wraps

from datetime import datetime, timedelta, timezone


# Error Handling
def error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}:")
            import traceback

            print(traceback.format_exc())
            raise

    return wrapper


# MAIN TODO
# 1. Make basic calls to graph from javascript and then flutter code
# 2. make test calls using config object and verify the chat thread histories are different


# === Load Environment Variables (.env) ===
load_dotenv()


# === Graph State ===
# All Graph Nodes must accept this type
# Any inputs to Graph must be of this type


graph_builder = StateGraph(AgentState, ConfigSchema)


# Thoughts
# How should tool structuring be done?
# Should ai execute all tools immediately ... if not what should the response from the tools to indicate the status
# Similarly how might we implement user confirmation of task calls?


# === Define LLM ===
# Consider Routing: https://console.groq.com/docs/tool-use#routing-system

# tool-user-preview model overeager tool call
# https://groq.com/pricing/
# llm = ChatGroq(model="llama3-groq-8b-8192-tool-use-preview")
llm = ChatGroq(model="llama3-groq-70b-8192-tool-use-preview")

# this model is more balanced
# model still fails at basic tasks - calling tools too aggressively
# llm = ChatGroq(model="llama-3.1-8b-instant")

# claude-3-5-sonnet is better, but very expensive
# https://console.anthropic.com/settings/billing
# llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

llm_with_tools = llm.bind_tools(get_all_tools(), parallel_tool_calls=False)


def chatbot(state: AgentState, config: RunnableConfig):

    # user_id = config["configurable"].get("user_id")
    # org_id = config["configurable"].get("org_id")

    # print("User ID: " + user_id)
    # print("Org ID: " + org_id)

    # if(user_id is None or org_id is None):
    #     return {"messages": [AIMessage(content="Warning - No user_id or org_id found in assistant config")]}

    # Return config variables to check they are received
    # return {"messages" : AIMessage(content= "user_id: " + user_id + " org_id: " + org_id)}

    # Get last 3 messages
    messages: list[BaseMessage] = trim_messages(
        state["messages"],
        # only use last 6 messages
        strategy="last",
        token_counter=len,
        max_tokens=6,
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

    # First check that config vars are present
    if (
        config["configurable"].get("timezone_offset_minutes") is None
        or config["configurable"].get("language") is None
    ):
        return {
            "messages": [
                AIMessage(
                    content="Warning - No timezone_offset_minutes or language found in assistant config"
                )
            ]
        }

    # Calculate time of day from config
    timezone_offset_minutes = config["configurable"].get("timezone_offset_minutes")

    # Convert offset minutes to UTC timezone
    tz = timezone(timedelta(minutes=timezone_offset_minutes))
    current_datetime = datetime.now(tz).strftime("%A, %d %B %Y %H:%M:%S")

    language = config["configurable"].get("language")

    # Get ui context
    ui_context = state["ui_context"]

    # Add system message to prompt
    messages.insert(
        0,
        SystemMessage(
            content="""
        Keep answers short as possible. 
        For tool parameters DATE_LIST, you should provide a List of days to get in YYYY/MM/DD format. Use YYYY/MM/DD - YYYY/MM/DD to get between two dates.
        For tool parameters STRICT_ENUM, you must only provide a value from the list of options provided. If user gives slightly different input map it to the correct value.
        The current date and time is: {}
        Prefer using language: {}
        Current UI Context: {}""".format(
                current_datetime, language, ui_context
            )
        ),
    )

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# TODO work on tool execution conditional branching
def check_ai_request(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]

    if not isinstance(last_message, ToolMessage):
        return END
    elif last_message.name in get_ai_request_tools():
        return "execute_ai_request_on_client"
    else:
        return END


# TODO : rename from show only and continue execution
# Determine how ai will either continue execcution or end here ...
def check_ai_result(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]

    if not isinstance(last_message, ToolMessage):
        return END
    else:
        return "run_with_result"


# Fake node to ask client
# I think - because we interrupt here - it allows us to resume ai execution
# By passing in empty message, otherwise nothing would happen
def execute_ai_request_on_client(state: AgentState):
    pass


graph_builder.add_node("chatbot", chatbot)


graph_builder.add_conditional_edges(
    "chatbot", tools_condition, {"tools": "tools", END: END}
)

graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "tools",
    check_ai_request,
    {"execute_ai_request_on_client": "execute_ai_request_on_client", END: END},
)

graph_builder.add_edge("tools", END)

graph_builder.add_node("execute_ai_request_on_client", execute_ai_request_on_client)

graph_builder.add_conditional_edges(
    "execute_ai_request_on_client",
    check_ai_result,
    {"run_with_result": "chatbot", END: END},
)

# graph_builder.set_entry_point("chatbot")
graph_builder.add_edge(START, "chatbot")


graph_builder.add_edge("chatbot", END)

# === Compile Graph ===
# No memory is needed for cloud
graph = graph_builder.compile(
    interrupt_before=["execute_ai_request_on_client"],
)