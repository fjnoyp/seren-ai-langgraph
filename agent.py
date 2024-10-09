from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq


from typing_extensions import TypedDict
from dotenv import load_dotenv

from typing import Annotated

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

from langchain_core.messages import AIMessage, ToolMessage, HumanMessage

from langchain_core.messages.tool import ToolCall


# === Load Environment Variables (.env) ===
load_dotenv()


# === Graph State ===
# All Graph Nodes must accept this type
# Any inputs to Graph must be of this type 
class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# === Define Tools ===
tool = TavilySearchResults(max_results=2)
tools = [tool]

graph_builder.add_node("tools", ToolNode(tools=[tool]))


# === Define LLM ===
# Consider Routing: https://console.groq.com/docs/tool-use#routing-system

# tool-user-preview model overeager tool call
#llm = ChatGroq(model="llama3-groq-8b-8192-tool-use-preview")

# this model is more balanced
llm = ChatGroq(model="llama-3.1-8b-instant")

# claude-3-5-sonnet is better, but very expensive 
#llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

llm_with_tools = llm.bind_tools(tools)


# === Define Graph Nodes === 
def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

graph_builder.add_node("chatbot", chatbot)

def select_next_node(state: State):
    return tools_condition(state)

graph_builder.add_conditional_edges(
    "chatbot",
    select_next_node,
    {"tools": "tools", END: END}
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")

# TODO - swap with postgres memory 
memory = MemorySaver()
graph = graph_builder.compile(
    checkpointer=memory,
)




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
