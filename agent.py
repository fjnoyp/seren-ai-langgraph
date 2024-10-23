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

from pydantic import BaseModel, Field

# MAIN TODO 
# 1. Make basic calls to graph from javascript and then flutter code 
# 2. make test calls using config object and verify the chat thread histories are different


# === Load Environment Variables (.env) ===
load_dotenv()


# === Graph State ===
# All Graph Nodes must accept this type
# Any inputs to Graph must be of this type 
class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# === Define Tools ===
tavily = TavilySearchResults(max_results=2)


# Add tools 
# Note: llama keeps hallucinating a "brave_search" tool that doesn't exist 

# To view the schema: create_task.args_schema.schema()
@tool(return_direct=True)
def request_to_create_task(
    task_name: Annotated[str, ""],
) -> str:
    """Create a task"""
    return f"Requested to create task: {task_name}"

@tool
def find_task(
    task_name: Annotated[str, ""]
) -> str:
    """Find a task"""
    return f"Found task: {task_name}"

@tool
def update_task_status(
    task_name: Annotated[str, ""],
    task_status: Annotated[str, "Must be: open, in_progress, or closed"]
) -> str:
    """Update a task status"""
    return f"Updated task: {task_name} with status: {task_status}"

@tool(return_direct=True)
def request_to_delete_task(
    task_name: Annotated[str, ""]
) -> str:
    """Delete a task"""
    return f"Requested to delete task: {task_name}"


tools = [request_to_create_task, find_task, update_task_status, request_to_delete_task]

graph_builder.add_node("tools", ToolNode(tools))

# Thoughts 
# How should tool structuring be done? 
# Should ai execute all tools immediately ... if not what should the response from the tools to indicate the status 
# Similarly how might we implement user confirmation of task calls? 


# === Define LLM ===
# Consider Routing: https://console.groq.com/docs/tool-use#routing-system

# tool-user-preview model overeager tool call
#llm = ChatGroq(model="llama3-groq-8b-8192-tool-use-preview")

# this model is more balanced
# model still fails at basic tasks - calling tools too aggressively 
#llm = ChatGroq(model="llama-3.1-8b-instant")

# claude-3-5-sonnet is better, but very expensive 
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
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

def select_next_node(state: State):
    return tools_condition(state)

graph_builder.add_conditional_edges(
    "chatbot",
    select_next_node,
    {"tools": "tools", END: END}
)

# TODO work on tool execution 
def tool_execution(state: State):
    return END
graph_builder.add_conditional_edges(
    "tools", 
    tool_execution,
    {END: END}
)

graph_builder.set_entry_point("chatbot")



# === Checkpointer ===
# TODO - swap with postgres memory 
checkpointer = MemorySaver()


# from psycopg import Connection
# from langgraph.checkpoint.postgres import PostgresSaver



# with Connection.connect(DB_URI, **connection_kwargs) as conn:
#     checkpointer = PostgresSaver(conn)
#     # NOTE: you need to call .setup() the first time you're using your checkpointer
#     # checkpointer.setup()
#     graph = create_react_agent(model, tools=tools, checkpointer=checkpointer)
#     config = {"configurable": {"thread_id": "2"}}
#     res = graph.invoke({"messages": [("human", "what's the weather in sf")]}, config)

#     checkpoint_tuple = checkpointer.get_tuple(config)
 

graph = graph_builder.compile(
    checkpointer=checkpointer,
)



# === LangGraphCloud Message Format ===
# Must match the state format 
# ex: 
example = [
  {
    "role" : "human",
    "content" : "how are you?"
  }
]




# === Run Graph === 

# For now we hardcode the config object used 
# Config is auto updated by the graph 
config = {"configurable": {"thread_id": "1"}}

from langchain_core.messages.base import BaseMessage

# Use for testing to allow insertion of messages into the graph
def run_ai_with_messages(messages: list[BaseMessage]) -> list[BaseMessage]:
    events = graph.stream(
        State(messages=messages), config, stream_mode="values"
    )

    # Print out current state of graph: 
    #snapshot = graph.get_state(config)
    #print(snapshot)

    messages_list = []
    for event in events:
        if "messages" in event:
            last_message = event["messages"][-1]
            messages_list.append(last_message)
    
    return messages_list


def run_ai_with_user_input(user_input: str) -> list[BaseMessage]:
    return run_ai_with_messages([HumanMessage(content=user_input)])

def run_ai_with_custom_input(input: str) -> list[BaseMessage]:
    # split the input by |
    chunks = input.split('|')
    messages = []
    
    for chunk in chunks:
        chunk = chunk.strip()
        if chunk.lower().startswith('tool:'):
            # Create a tool message
            tool_content = chunk[5:].strip()  # Remove 'tool:' prefix
            messages.append(ToolMessage(
                content=tool_content,
                # TODO - get the proper tool call id! 
                tool_call_id=''
                ))
        else:
            # Create a human message
            messages.append(HumanMessage(content=chunk))
    
    return run_ai_with_messages(messages)