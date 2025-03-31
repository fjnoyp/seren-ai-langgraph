from src.llm_config import llm, llm_with_tools

from langchain_core.messages import (
    AIMessage,
    SystemMessage,
    trim_messages,
)

from src.agent_state import AgentState

from datetime import datetime, timedelta, timezone

from langchain_core.runnables.config import RunnableConfig
from langgraph.types import Command


def node_tool_caller(state: AgentState, config: RunnableConfig):
    """Call a tool call based on the plan"""
    messages = state["messages"]
    plan = state.get("plan", "")
    prev_node_feedback = state.get("prev_node_feedback")

    # Get context information
    timezone_offset_minutes = config["configurable"].get("timezone_offset_minutes", 0)
    tz = timezone(timedelta(minutes=timezone_offset_minutes))
    current_datetime = datetime.now(tz).strftime("%A, %d %B %Y %H:%M:%S")
    ui_context = state.get("ui_context", "")

    # Create system message for tool execution
    system_content = f"""
    You MUST respond with a proper tool call.

    Call a tool based on: 
    {prev_node_feedback}

    PLAN CONTEXT:
    {plan}

    INSTRUCTIONS:
    - Analyze the context and determine the appropriate parameters for this tool
    - Use ONLY structured tool calls
    - Include ONLY the tool call without additional explanation

    Prefer using the same language as the user's query. 

    All dates should be in ISO 8601 format.

    If user refers to self, use keyword MYSELF in the assigned_user_names call.     
    
    The current date and time is: {current_datetime}    

    Current UI Context: {ui_context}
    """

    # Get minimal context (just the last few messages)
    context_messages = trim_messages(
        messages,
        strategy="last",
        token_counter=len,
        max_tokens=5,
        start_on="human",
        end_on=("human", "ai"),
        include_system=False,
    )

    # Add the system message
    system_message = SystemMessage(content=system_content)
    context_messages = [system_message] + context_messages

    try:
        # Generate tool call
        response = llm_with_tools.invoke(context_messages)

        # Check if tool call was actually made
        if isinstance(response, AIMessage) and response.tool_calls:
            # Success - return the message
            return {
                "messages": [response],
                "prev_node_feedback": "",
                "iteration_count": state.get("iteration_count", 0) + 1,
                "next_node": "",
            }
        else:
            # No tool call made
            return Command(
                goto="tools",
                update={
                    "prev_node_feedback": f"ERROR: You must call a tool in the tool_calls output and not respond via content! Please try again: {prev_node_feedback}",
                    "iteration_count": state.get("iteration_count", 0) + 1,
                    "next_node": "tool_caller",
                },
            )
    except Exception as e:
        # Exception during tool call
        return Command(
            goto="planner",
            update={
                "prev_node_feedback": f"ERROR: Exception during tool call: {str(e)}",
                "iteration_count": state.get("iteration_count", 0) + 1,
                "next_node": "",
            },
        )
