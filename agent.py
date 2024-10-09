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


# Load environment variables from .env file
load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

tool = TavilySearchResults(max_results=2)
tools = [tool]

graph_builder.add_node("tools", ToolNode(tools=[tool]))


# Groq suggests routing between normal model and tool specialized models
# https://console.groq.com/docs/tool-use#routing-system

# tool-user-preview model is over eager in calling tools, will use web search tool to summarize a conversation ... 
#llm = ChatGroq(model="llama3-groq-8b-8192-tool-use-preview")

# this model is much better .. 
llm = ChatGroq(model="llama-3.1-8b-instant")

#llm = ChatOpenAI(model="gpt-3.5-turbo")

# claude-3-5-sonnet is better, but very expensive 
#llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

llm_with_tools = llm.bind_tools(tools)

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

from langchain_core.messages.base import BaseMessage

# Use for testing to allow insertion of messages into the graph
def run_ai_with_messages(messages: list[BaseMessage]) -> list[BaseMessage]:
    # The config is the **second positional argument** to stream() or invoke()!
    events = graph.stream(
        State(messages=messages), config, stream_mode="values"
    )

    # answer calculated print out the config
    #snapshot = graph.get_state(config)
    #print(snapshot)

    messages_list = []
    for event in events:
        if "messages" in event:
            last_message = event["messages"][-1]
            messages_list.append(last_message)
    
    return messages_list


def run_ai(user_input: str) -> list[BaseMessage]:
    return run_ai_with_messages([HumanMessage(content=user_input)])








# Read in Langsmith data 
# Parse it into the same format as above
from langsmith import Client

client = Client()

dataset_name = "initial-test"
examples = client.list_examples(dataset_name=dataset_name)

import json



# TODO - do the actual evaluation 
from langsmith import Client
from langsmith.schemas import Run, Example
from langsmith.evaluation import evaluate
import openai
from langsmith.wrappers import wrap_openai

# Define AI system

def predict(inputs: dict) -> dict:
    messages = inputs["messages"]
    return State(messages=run_ai_with_messages(messages))


# Define evaluators
# import json

# def test_evaluator(run: Run, example: Example) -> dict:

#     # Ref output is in Langsmith dictionary Format 
#     ref_output = example.outputs.get("messages")

#     # Cur output is in BaseMessage Format 
#     cur_output = run.outputs.get("messages")

#     # Pretty print the reference and current output in JSON format
#     print("Reference Output:", json.dumps(ref_output, indent=4))

#     # Breaks - BaseMessage is not JSON serializable    
#     #print("Current Output:", json.dumps(cur_output, indent=4))

#     return {"key": "test_evaluator","score": 1.0}

# experiment_results = evaluate(
#     predict, # Your AI system
#     data=dataset_name, # The data to predict and grade over
#     evaluators=[test_evaluator], # The evaluators to score the results
#     experiment_prefix="test",
#     metadata={
#         "version": "0.0.1",
#     },
# )




config = {"configurable": {"thread_id": "1"}}

# To debug graph state run:
# graph.get_state(config) 


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        results = run_ai(user_input)
        print(results[-1].pretty_print())        
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        results = run_ai(user_input)
        print(results[-1].pretty_print())        
        break
