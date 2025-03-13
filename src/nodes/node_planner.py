import json
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

# Import llm from llm_config
from src.llm_config import llm

from typing import Literal, Optional

from langgraph.graph.message import add_messages

from pydantic import BaseModel, Field

from langchain_core.messages import (
    SystemMessage,
    trim_messages,
)

from src.agent_state import AgentState

from src.tools.tools import get_all_tools

from datetime import datetime, timedelta, timezone

from langgraph.types import Command


class PlannerDecision(BaseModel):
    """Decision output from the planning node"""

    plan: str = Field(
        description="Plan of what's been done and everything that still needs to be done"
    )

    next_node: str = Field(
        description="Which ai node to run next, MUST BE ONLY 'tool_caller' to call a tool, or 'response_generator' for generating a message for the user to see."
    )
    next_node_instructions: str = Field(
        description="Instructions to the next ai node what needs to be done next"
    )


def node_planner(state: AgentState, config):
    """Create a plan before executing any tools"""
    messages = state["messages"]
    current_plan = state.get("plan", "")
    prev_node_feedback = state.get("prev_node_feedback", "")
    iteration_count = state.get("iteration_count", 0)

    # Cap iterations to prevent infinite loops
    if iteration_count > 10:
        return {
            "next_node": "response_generator",
            "prev_node_feedback": "MAX ITERATIONS REACHED",
        }

    # Get context information
    # timezone_offset_minutes = config["configurable"].get("timezone_offset_minutes", 0)
    # tz = timezone(timedelta(minutes=timezone_offset_minutes))
    # current_datetime = datetime.now(tz).strftime("%A, %d %B %Y %H:%M:%S")
    ui_context = state.get("ui_context", "")

    # Create available tools list - simplified to just names and descriptions
    available_tools = []
    for tool in get_all_tools():
        available_tools.append({"name": tool.name, "description": tool.description})

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

    # Create planning system message
    system_content = f"""
    You coordinate a plan and determine which ai needs to run next to perform that plan. 

    The user sees the following UI - this might affect what they want to do next: {ui_context}
    
    Last Plan: {current_plan}

    Previous Node Feedback: {prev_node_feedback}
    
    CURRENT ITERATION: {iteration_count + 1}/10
    
    AVAILABLE TOOLS the tool ai can use: 
    {json.dumps(available_tools, indent=2)}
    
    Your job is to:
    1. UPDATE the current plan based on the conversation and any feedback
    2. DECIDE which ai should run next, and provide detailed instructions to them what to do. 

    For next_node, you MUST ONLY use one of these exact values:
    - "tool_caller" - when a tool needs to be called
    - "response_generator" - when a response should be generated for the user
    """

    # Add system message
    system_message = SystemMessage(content=system_content)
    planning_messages = [system_message] + context_messages

    # Use structured output to get planning decision
    planner_llm = llm.with_structured_output(PlannerDecision)
    decision = planner_llm.invoke(planning_messages)

    print(f"DEBUG - LLM returned next_node: '{decision.next_node}'")
    return {
        "plan": decision.plan,
        "next_node": decision.next_node,
        "prev_node_feedback": decision.next_node_instructions,
        "iteration_count": iteration_count + 1,
    }
