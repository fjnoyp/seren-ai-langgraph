from enum import Enum
from langchain_core.tools import tool
from typing import Annotated
import json

from src.tools.ai_tool_response_models import AiActionRequestModel, AiActionRequestType, AiInfoRequestModel, AiInfoRequestType
from src.tools.tool_context_manager import tool_context

# Tools called by AI to interact with a user's shifts 
# 

# === SHIFT TOOLS ===
# 1) Get current shift
# 2) Clock in / out of current shift
# 3) Get shift history for specific day
# 4) Ask questions about shifts?

@tool()
def get_current_shift_info(show_only: Annotated[bool, "If True, only shows the shift info without further actions"] = False) -> str:
    """Gets information about the current shift."""
    response = AiInfoRequestModel(
        info_request_type=AiInfoRequestType.CURRENT_SHIFT,
        show_only=show_only
    )
    return json.dumps(response.to_dict())

@tool()
def clock_in_or_out(clock_in: Annotated[bool, "If True, clocks in. If False, clocks out."]) -> str: 
    """Clock in or out of the current shift."""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.CLOCK_IN if clock_in else AiActionRequestType.CLOCK_OUT
    )
    return json.dumps(response.to_dict())

def get_all_tools():
    return [get_current_shift_info, clock_in_or_out]

def get_ai_request_tools():
    return [get_current_shift_info, clock_in_or_out]


