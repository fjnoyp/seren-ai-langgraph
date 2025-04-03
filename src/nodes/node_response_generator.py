from src.llm_config import llm
from langchain_core.messages import (
    SystemMessage,
    trim_messages,
)
from pydantic import BaseModel, Field
from src.agent_state import AgentState
from langchain_core.runnables.config import RunnableConfig
from datetime import datetime, timedelta, timezone


class FinalResponse(BaseModel):
    """Final response to the user"""

    response: str = Field(description="The response to provide to the user")


def node_response_generator(state: AgentState, config: RunnableConfig):
    """Generate a response based on the plan"""
    messages = state["messages"]
    plan = state.get("plan", "")
    prev_node_feedback = state.get("prev_node_feedback", "")

    # Get context information
    timezone_offset_minutes = config["configurable"].get("timezone_offset_minutes", 0)
    tz = timezone(timedelta(minutes=timezone_offset_minutes))
    current_datetime = datetime.now(tz).strftime("%A, %d %B %Y %H:%M:%S")
    ui_context = state.get("ui_context", "")

    # Create system message for response generation
    system_content = f"""
    YOUR ROLE: You are the final communication layer that synthesizes information and presents it to the user in a clear, natural way.
    
    IMPORTANT CONTEXT:
    - Plan summary: {plan}
    - Previous node information: {prev_node_feedback}
    - Current UI context: {ui_context}
    - Current time: {current_datetime}
    
    YOUR TASK:
    1. Analyze the conversation and all available information
    2. Extract the key results and actions that have been performed
    3. Synthesize a natural, helpful response that:
       - Directly answers the user's original query
       - DOES NOT REPEAT anything mentioned in a previous message for the user (unless it's very important)
       - Explains what actions were taken on their behalf
       - Presents information in a clear, organized way
       - Uses natural language (not technical jargon or raw function calls)
       - Matches the user's language style
    
    CRITICAL REQUIREMENTS:
    - NEVER show raw function calls, JSON, or technical syntax to the user
    - NEVER mention the internal planning process or node names
    - NEVER refer to "tools" or "functions" in your response
    - DO translate technical operations into human terms (e.g., "I've created a task" instead of "create_task function called")
    - DO respond naturally as if you performed all the actions yourself
    - DO focus on providing clear value and information the user requested
    - DO keep responses concise yet complete
    
    If you find tool results in the message history, interpret and explain them in natural language.
    """

    # Get recent message context - include more context to ensure we have enough information
    context_messages = trim_messages(
        messages,
        strategy="last",
        token_counter=len,
        max_tokens=12,  # Increased context window
        start_on="human",
        include_system=False,
    )

    # Add the system message
    system_message = SystemMessage(content=system_content)
    response_messages = [system_message] + context_messages

    try:
        # Generate response directly as an AIMessage without structured output
        response = llm.invoke(response_messages)

        # Return response message
        return {
            "messages": [response],
            "plan": "",
            "prev_node_feedback": "",
            "iteration_count": 0,
            "next_node": "",
        }  # Clear tool result
    except Exception as e:
        # Return error without adding a message
        return {"tool_result": f"ERROR: Exception during response generation: {str(e)}"}
