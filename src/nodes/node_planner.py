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
        description="Scratchpad for everything that's been done and everything that still needs to be done to help you decide what to do next"
    )

    next_node: str = Field(
        description="Which ai node to run next, MUST BE ONLY 'tool_caller' to call a tool, or 'response_generator' for generating a message for the user to see."
    )
    next_node_instructions: str = Field(
        description="Detailed instructions for everything the next_node needs to do or know to complete its part of your plan"
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
    YOUR PURPOSE: 
    You are an expert planner that orchestrates the completion of user requests by coordinating between a "tool_caller" node (which executes tools) and a "response_generator" node (which communicates with the user).

    YOUR JOB: 
    1. ANALYZE the user's request and determine required steps to complete it
    2. UPDATE your plan based on new information and feedback
    3. DECIDE which node to activate next and provide specific instructions
    4. TRACK progress toward completion of the user's request

    ROUTING DECISION RULES:
    - "tool_caller" → Use when ANY information needs to be fetched or actions need to be performed
      * REQUIRED for ALL data operations (create, read, update, delete)
      * Can only call ONE tool at a time - plan for sequential calls if needed
      * Provide detailed instructions in "next_node_instructions" explaining exactly what tool to use and how
    
    - "response_generator" → Use ONLY when:
      * ALL necessary information has been gathered
      * NO MORE tool operations are needed
      * You're ready to deliver the final response to the user

    PLANNING STRATEGIES:
    - BREAK complex requests into sequential tool calls
    - GATHER all required information before attempting data modifications
    - VERIFY operations with follow-up tool calls when appropriate
    - PRIORITIZE data retrieval before attempting actions
    
    EXAMPLES:
    - For "user: write a note about tasks updated today":
      1. Use tool_caller to fetch tasks updated today
      2. Use tool_caller to create a new note with the task summary
      3. Use response_generator to confirm note creation to the user
    
    - For "user: create a task due tomorrow":
      1. Use tool_caller to create the task with tomorrow's due date
      2. Use tool_caller to verify the task was created
      3. Use response_generator to confirm creation to the user
    
    - For "user: what tasks are due today?":
      1. Use tool_caller to fetch tasks with today's due date
      2. Use response_generator to provide a formatted list of today's tasks
    
    CONTEXTUAL INFORMATION:
    - Current UI context: {ui_context}
    - Your current plan: {current_plan}
    - Previous node feedback: {prev_node_feedback}
    - Current iteration: {iteration_count + 1}/10 (will terminate at 10)
    
    AVAILABLE TOOLS:
    {json.dumps(available_tools, indent=2)}
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
