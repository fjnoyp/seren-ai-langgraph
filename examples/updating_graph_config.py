from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain_core.messages.tool import ToolCall

# Example of manually updating the graph history state 
# For usage with Langsmith datasets

config = {"configurable": {"thread_id": "1"}}

# Correct format, now see how we can load same format from langsmith dataset 
new_messages = [
    HumanMessage(content="Hello, my name is Kyle, what is the weather today"),
    AIMessage(content="Hello Kyle, the weather is rainy today"),
    HumanMessage(content="I need some expert guidance for building this AI agent. Could you request assistance for me?"),
    AIMessage(
        content="",
        tool_calls=[
            ToolCall(
                name="RequestAssistance", 
                args={"request": "guidance for building this AI agent"},
                id="123"
            )
        ],
    ),
    ToolMessage(
        tool_call_id="123",
        content="No response from human."),
    AIMessage(content="It seems like there's no immediate expert available. Would you like me to look up some information on building AI agents instead?"),
]

#new_messages[-1].pretty_print()

# graph.update_state(
#     # Which state to update
#     config,
#     # The updated values to provide. The messages in our `State` are "append-only", meaning this will be appended
#     # to the existing state. We will review how to update existing messages in the next section!
#     {"messages": new_messages},
# )