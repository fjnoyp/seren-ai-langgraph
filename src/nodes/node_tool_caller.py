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

    # Set maximum retry attempts
    max_retries = 3
    current_attempt = 0
    last_error = ""

    # Local retry loop
    while current_attempt < max_retries:
        current_attempt += 1

        # Add retry guidance if this isn't the first attempt
        retry_guidance = ""
        if current_attempt > 1:
            retry_guidance = f"""
            RETRY ATTEMPT {current_attempt}/{max_retries}
            
            Previous attempt failed: {last_error}
            
            CRITICAL REQUIREMENTS:            
            - You MUST use a tool call format (not plain text)
            - Your response MUST include a properly formatted tool call
            - DO NOT return an empty response or empty tool call            
            """

        # Create system message for tool execution
        system_content = f"""
        YOUR PURPOSE:
        You are a tool executor that translates instructions into precise tool calls. 

        CURRENT TASK:
        {prev_node_feedback}

        REQUIREMENTS:
        - SELECT the appropriate tool for the task
        - PROVIDE all required parameters for the selected tool
        - DO NOT return an empty response

        {retry_guidance}

        FORMATTING GUIDELINES:
        - Use the same language as in the user's request
        - Format dates in ISO 8601 format (YYYY-MM-DD)
        - If user refers to themselves, use keyword MYSELF in user assignments
        - Set show_to_user=False for background operations or intermediate steps
        
        CONTEXTUAL INFORMATION:
        - Current date/time: {current_datetime}
        - UI Context: {ui_context}
        """

        # Get minimal context (just the last few messages)
        context_messages = trim_messages(
            messages,
            strategy="last",
            token_counter=len,
            max_tokens=5,
            start_on="human",
            # This appears to be causing important last message to be lost (like tool execution results from a multi step ai request)
            # end_on=("human", "ai"),
            include_system=False,
        )

        # Add the system message
        system_message = SystemMessage(content=system_content)
        context_messages = [system_message] + context_messages

        try:
            # Generate tool call
            response = llm_with_tools.invoke(context_messages)

            # Check if tool call was actually made and is not empty
            if (
                isinstance(response, AIMessage)
                and response.tool_calls
                and len(response.tool_calls) > 0
                and response.tool_calls[0].get("name")
            ):

                # Success - return the message
                print(f"Tool call successful on attempt {current_attempt}")
                return {
                    "messages": [response],
                    "prev_node_feedback": "",
                    "iteration_count": state.get("iteration_count", 0) + 1,
                    "next_node": "tools",
                }
            else:
                # Tool call was not made or is invalid
                if isinstance(response, AIMessage):
                    if not response.tool_calls:
                        last_error = "No tool call was made"
                    elif len(response.tool_calls) == 0:
                        last_error = "Empty tool calls array"
                    else:
                        last_error = "Tool call missing required information"
                else:
                    last_error = "Unexpected response format"

                print(f"Attempt {current_attempt} failed: {last_error}")
                continue  # Try again

        except Exception as e:
            # Exception during tool call
            last_error = f"Exception occurred: {str(e)}"
            print(f"Attempt {current_attempt} failed with exception: {str(e)}")
            continue  # Try again

    # If we've reached here, all retry attempts failed
    print(f"All {max_retries} retry attempts failed, returning to planner")
    return {
        "prev_node_feedback": f"ERROR: After {max_retries} attempts, the system failed to generate a valid tool call. Last error: {last_error}. Please try a different approach.",
        "iteration_count": state.get("iteration_count", 0) + 1,
        "next_node": "planner",
    }
