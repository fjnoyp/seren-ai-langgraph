import json
from langchain_core.tools import tool
from typing import Annotated, Optional

from src.tools.ai_request_models import (
    AiActionRequestModel,
    AiActionRequestType,
    AiInfoRequestModel,
    AiInfoRequestType,
)

# === TASK TOOLS ===


@tool
def create_task(
    task_name: Annotated[str, ""],
    task_description: Annotated[Optional[str], ""] = None,
    task_start_date: Annotated[Optional[str], ""] = None,
    task_due_date: Annotated[Optional[str], ""] = None,
    task_priority: Annotated[
        Optional[str], "Must be: veryLow, low, normal, high, veryHigh"
    ] = None,
    task_status: Annotated[
        Optional[str], "Must be: open, inProgress, or closed"
    ] = None,
    estimate_duration_minutes: Annotated[Optional[int], 0] = None,
    assigned_user_names: Annotated[Optional[list[str]], ""] = None,
    parent_project_name: Annotated[Optional[str], ""] = None,
) -> str:
    """Create a task"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.CREATE_TASK,
        args={
            "task_name": task_name,
            "task_description": task_description,
            "task_start_date": task_start_date,
            "task_due_date": task_due_date,
            "task_priority": task_priority,
            "task_status": task_status,
            "estimate_duration_minutes": estimate_duration_minutes,
            "assigned_user_names": assigned_user_names,
            "parent_project_name": parent_project_name,
        },
    )
    return json.dumps(response.to_dict())


@tool
def add_comment_to_task(
    task_name: Annotated[str, ""],
    comment: Annotated[str, ""],
) -> str:
    """Add a comment to a task"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.ADD_COMMENT_TO_TASK,
        args={
            "task_name": task_name,
            "comment": comment,
        },
    )
    return json.dumps(response.to_dict())


@tool
def find_tasks(
    task_name: Annotated[Optional[str], ""] = None,
    task_description: Annotated[Optional[str], ""] = None,
    task_due_date_start: Annotated[
        Optional[str], "Get all tasks due after this date"
    ] = None,
    task_due_date_end: Annotated[
        Optional[str], "Get all tasks due before this date"
    ] = None,
    task_created_date_start: Annotated[
        Optional[str], "Get all tasks created after this date"
    ] = None,
    task_created_date_end: Annotated[
        Optional[str], "Get all tasks created before this date"
    ] = None,
    # task_due_dates_to_get: Annotated[
    #     Optional[list[str]], "Due dates of tasks to get"
    # ] = None,
    # task_created_dates_to_get: Annotated[
    #     Optional[list[str]], "Created dates of tasks to get"
    # ] = None,
    task_status: Annotated[
        Optional[str], "Must be: open, inProgress, or closed - STRICT_ENUM"
    ] = None,
    task_priority: Annotated[
        Optional[str],
        "Must be: veryLow, low, normal, high, veryHigh - STRICT_ENUM",
    ] = None,
    estimate_duration_minutes: Annotated[Optional[int], ""] = None,
    parent_project_name: Annotated[Optional[str], ""] = None,
    author_user_name: Annotated[Optional[str], ""] = None,
    assigned_user_names: Annotated[Optional[list[str]], ""] = None,
    # get_overdue_tasks_only: Annotated[Optional[bool], ""] = None,
) -> str:
    """Find tasks"""
    response = AiInfoRequestModel(
        info_request_type=AiInfoRequestType.FIND_TASKS,
        args={
            "task_name": task_name,
            "task_description": task_description,
            # TODO - remove - send fields for backwards compatibility
            "task_due_date": None,
            "task_created_date": None,
            "date_search_radius_days": None,
            "task_status": task_status,
            "task_priority": task_priority,
            "estimate_duration_minutes": estimate_duration_minutes,
            "parent_project_name": parent_project_name,
            "author_user_name": author_user_name,
            "assigned_user_names": assigned_user_names,
            # "task_due_dates_to_get": task_due_dates_to_get,
            # "task_created_dates_to_get": task_created_dates_to_get,
            "task_due_date_start": task_due_date_start,
            "task_due_date_end": task_due_date_end,
            "task_created_date_start": task_created_date_start,
            "task_created_date_end": task_created_date_end,
            # "get_overdue_tasks_only": get_overdue_tasks_only,
        },
    )
    return json.dumps(response.to_dict())


@tool
def update_task_fields(
    task_name: Annotated[str, ""],
    task_description: Annotated[Optional[str], ""] = None,
    task_start_date: Annotated[Optional[str], ""] = None,
    task_due_date: Annotated[Optional[str], ""] = None,
    task_status: Annotated[
        Optional[str], "Must be: open, inProgress, or closed - STRICT_ENUM"
    ] = None,
    task_priority: Annotated[
        Optional[str],
        "Must be: veryLow, low, normal, high, veryHigh - STRICT_ENUM",
    ] = None,
    estimate_duration_minutes: Annotated[Optional[int], ""] = None,
    assigned_user_names: Annotated[Optional[list[str]], ""] = None,
    parent_project_name: Annotated[Optional[str], ""] = None,
) -> str:
    """Update fields of a task"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.UPDATE_TASK_FIELDS,
        args={
            "task_name": task_name,
            "task_description": task_description,
            "task_due_date": task_due_date,
            "task_start_date": task_start_date,
            "task_status": task_status,
            "task_priority": task_priority,
            "estimate_duration_minutes": estimate_duration_minutes,
            "assigned_user_names": assigned_user_names,
            "parent_project_name": parent_project_name,
        },
    )
    return json.dumps(response.to_dict())


@tool
def delete_task(task_name: Annotated[str, ""]) -> str:
    """Delete a task"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.DELETE_TASK,
        args={"task_name": task_name},
    )
    return json.dumps(response.to_dict())


# Unused - use update_task_fields instead for now
# @tool
# def assign_user_to_task(
#     task_name: Annotated[str, ""],
#     user_name: Annotated[str, ""],
# ) -> str:
#     """Assign a user to a task"""
#     response = AiActionRequestModel(
#         action_request_type=AiActionRequestType.ASSIGN_USER_TO_TASK,
#         args={"task_name": task_name, "user_name": user_name},
#     )
#     return json.dumps(response.to_dict())


def get_tools():
    return [
        create_task,
        find_tasks,
        update_task_fields,
        delete_task,
        add_comment_to_task,
    ]


def get_ai_request_tools():
    return [
        create_task,
        find_tasks,
        update_task_fields,
        delete_task,
        add_comment_to_task,
    ]
