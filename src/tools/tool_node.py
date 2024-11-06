from langchain_core.runnables.config import RunnableConfig

from langgraph.prebuilt import ToolNode

from src.agent_state import AgentState

from src.tools import shift_tools

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
        # *task_tools.get_tools(),
        *shift_tools.get_all_tools(),
        # tavily,
    ]


def get_ai_request_tools():
    return [
        *shift_tools.get_ai_request_tools(),
    ]

# graph_builder.add_node("tools", ToolNode(tools))


def tool_node(state: AgentState): #, config: RunnableConfig):
    # user_id = config["configurable"].get("user_id")
    # org_id = config["configurable"].get("org_id")

    # Set the tool context with user and org information (UNUSED FOR NOW - as ai makes requests to client directly instead)
    # with set_tool_context({"user_id": user_id, "org_id": org_id}):
    return ToolNode(get_all_tools()).invoke(state) #, config)
