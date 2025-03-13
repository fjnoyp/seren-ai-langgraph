from langchain_core.runnables.config import RunnableConfig

from langgraph.prebuilt import ToolNode

from src.agent_state import AgentState

from src.config_schema import ConfigSchema
from src.tools import shift_tools, task_tools

from langchain_community.tools.tavily_search import TavilySearchResults

from src.tools.tool_context_manager import set_tool_context


# ==================
# === TOOLS ===
# ==================

# === TAVILY TOOL ===
tavily = TavilySearchResults(max_results=2)


# === SHIFTS TOOL ===
# Goal: get current shift / clock in or out of current shift / get shift history for specific day / ask questions about shifts?


def get_all_tools():
    return [
        *shift_tools.get_all_tools(),
        *task_tools.get_tools(),
        # tavily,
    ]


# Tools that route to execute_ai_request_on_client
# Only for tools that need followup UI execution (Mar 10 25 - we are disabling showOnly ..) the ai to respond again
def get_ai_request_tools():
    return [
        *shift_tools.get_ai_request_tools(),
        *task_tools.get_ai_request_tools(),
    ]


# graph_builder.add_node("tools", ToolNode(tools))
