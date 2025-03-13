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
    You need to generate a helpful response to the user.
    
    PLAN CONTEXT:
    {plan}
    
    PREVIOUS NODE FEEDBACK:
    {prev_node_feedback}
    
    INSTRUCTIONS:
    - Provide a direct, helpful response to the user's original query
    - If tools were used, include the information gathered or actions performed
    - Keep your response concise and to the point
    - DO NOT mention the internal planning process
    
    The current date and time is: {current_datetime}
    Respond in the same language as the user's query

    Current UI Context: {ui_context}
    """

    # Get recent message context
    context_messages = trim_messages(
        messages,
        strategy="last",
        token_counter=len,
        max_tokens=10,
        start_on="human",
        end_on=("human", "tool", "ai"),
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
