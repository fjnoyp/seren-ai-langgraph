from src.agent_state import AgentState
from src.agent import graph_builder  # Import the graph object
from langchain_core.messages import ToolMessage, HumanMessage

from langgraph.checkpoint.memory import MemorySaver


# === LangGraphCloud Message Format ===
# Must match the state format
# ex:
example = [{"role": "human", "content": "how are you?"}]


# === Run Graph ===
# TODO - should just switch to using the LangGraphCloud client (which we already do in Supabase JS)

# For now we hardcode the config object used
# Config is auto updated by the graph
config = {
    "configurable": {
        "user_id": "2758cac4-304a-46d8-941f-ef0277f0056a",
        "org_id": "a7666926-89b4-48d5-99ea-91189e3cab89",
        "timezone_offset_minutes": 0,
        "language": "en",
        "thread_id": "1",
    }
}

from langchain_core.messages.base import BaseMessage


# Build the Local Graph
local_graph = graph_builder.compile(
    interrupt_before=["execute_ai_request_on_client"],
    checkpointer=MemorySaver(),
)


# Use for testing to allow insertion of messages into the graph
def run_ai_with_messages(messages: list[BaseMessage]) -> list[BaseMessage]:
    events = local_graph.stream(
        # Issue - when sending message hi and ui context is provided, ai stupidly calls find task ....
        # AgentState(messages=messages, ui_context="current task name = Kill Bats"), config=config, stream_mode="values"
        AgentState(messages=messages, ui_context=""),
        config=config,
        stream_mode="values",
    )

    # Print out current state of graph:
    # snapshot = graph.get_state(config)
    # print(snapshot)

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
    chunks = input.split("|")
    messages = []

    for chunk in chunks:
        chunk = chunk.strip()
        if chunk.lower().startswith("tool:"):
            # Create a tool message
            tool_content = chunk[5:].strip()  # Remove 'tool:' prefix
            messages.append(
                ToolMessage(
                    content=tool_content,
                    # TODO - get the proper tool call id!
                    tool_call_id="",
                )
            )
        else:
            # Create a human message
            messages.append(HumanMessage(content=chunk))

    return run_ai_with_messages(messages)
