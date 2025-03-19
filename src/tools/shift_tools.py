from enum import Enum
from langchain_core.tools import tool
from typing import Annotated
import json

from src.tools.ai_request_models import (
    AiActionRequestModel,
    AiActionRequestType,
    AiInfoRequestModel,
    AiInfoRequestType,
)
from src.tools.tool_context_manager import tool_context

# Tools called by AI to interact with a user's shifts
#

# === SHIFT TOOLS ===
# 1) Get current shift
# 2) Clock in / out of current shift
# 3) Get shift history for specific day
# 4) Ask questions about shifts?


# get shift for week
# but what about overrides ...
# then need base time ...
# tomorrow / yesterday / next week / next month ?
# specific days / weeks / months ... ?
# we need a way to convert time references to actual times ...


@tool
def get_shift_assignments(
    daysToGet: Annotated[
        list[str], ""
    ],  # List of days to get in YYYY/MM/DD format. Use date - date to get between two dates" ],
    show_only: Annotated[
        bool, "If True, only shows the shift info without further actions"
    ] = False,
) -> str:
    """Get shift assignments (times you need to clock in/out of work) for specific days"""
    response = AiInfoRequestModel(
        info_request_type=AiInfoRequestType.SHIFT_ASSIGNMENTS,
        args={
            # TODO - remove - send fields for backwards compatibility
            "day_offsets_to_get": 0,
            # TODO - New field to support:
            "days_to_get": daysToGet,
        },
        show_only=show_only,
    )
    return json.dumps(response.to_dict())


@tool
def get_shift_logs(
    daysToGet: Annotated[
        list[str], ""
    ],  # List of days to get in YYYY/MM/DD format. Use date - date to get between two dates" ],
    show_only: Annotated[
        bool, "If True, only shows the shift info without further actions"
    ] = False,
) -> str:
    """Get shift logs (times you clocked in/out of work) for specific days"""
    response = AiInfoRequestModel(
        info_request_type=AiInfoRequestType.SHIFT_LOGS,
        args={
            # TODO - remove - send fields for backwards compatibility
            "day_offsets_to_get": 0,
            # TODO - New field to support:
            "days_to_get": daysToGet,
        },
        show_only=show_only,
    )
    return json.dumps(response.to_dict())


@tool()
def toggle_clock_in_or_out() -> str:
    """Clock in if not clocked in or out otherwise"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.TOGGLE_CLOCK_IN_OR_OUT
    )
    return json.dumps(response.to_dict())


def get_all_tools():
    return [get_shift_assignments, get_shift_logs, toggle_clock_in_or_out]


def get_ai_request_tools():
    return [get_shift_assignments, get_shift_logs, toggle_clock_in_or_out]


@tool()
def get_current_shift_info(
    show_only: Annotated[
        bool, "If True, only shows the shift info without further actions"
    ] = False,
) -> str:
    """Gets information about the current shift."""
    response = AiInfoRequestModel(
        info_request_type=AiInfoRequestType.CURRENT_SHIFT, show_only=show_only
    )
    return json.dumps(response.to_dict())
