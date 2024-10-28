from langchain_core.tools import tool
from typing import Annotated

from agent.tools.tool_context_manager import tool_context

# === SHIFT TOOLS ===
# 1) Get current shift
# 2) Clock in / out of current shift
# 3) Get shift history for specific day
# 4) Ask questions about shifts?

@tool(return_direct=True)
def get_current_shift() -> str:
    """ Get user's shift information"""

    context = tool_context.get()

    print(f'from shift_tools: {context}')

    print(f'from shift_tools: {context["user_id"]}')
    print(f'from shift_tools: {context["org_id"]}')

    """Get the current shift for a user"""
    return f"Current shift for user: {context['user_id']}"


def get_tools():
    return [get_current_shift]
