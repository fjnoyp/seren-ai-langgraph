import json
from langchain_core.tools import tool
from typing import Annotated, Optional

from src.tools.ai_request_models import AiActionRequestModel, AiActionRequestType, AiInfoRequestModel, AiInfoRequestType

# === TASK TOOLS ===

@tool
def create_task(
    task_name: Annotated[str, ""],
    task_description: Annotated[Optional[str], ""],
    task_due_date: Annotated[Optional[str], "Must be in ISO 8601 format"],    
    task_priority: Annotated[Optional[str], "Must be: veryLow, low, normal, high, veryHigh"],
    estimate_duration_minutes: Annotated[Optional[int], 0],
) -> str:    
    """Create a task"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.CREATE_TASK,
        args={
            "task_name": task_name,
            "task_description": task_description,
            "task_due_date": task_due_date,
            "task_priority": task_priority,
            "estimate_duration_minutes": estimate_duration_minutes,
        }
    )
    return json.dumps(response.to_dict())


@tool 
def find_tasks(
    task_name: Annotated[Optional[str], ""] = None,
    task_description: Annotated[Optional[str], ""] = None,
    task_due_date: Annotated[Optional[str], "Must be in ISO 8601 format"] = None,
    task_created_date: Annotated[Optional[str], "Must be in ISO 8601 format"] = None,
    date_search_radius_days: Annotated[Optional[int], "Set to search X amount of days from the task due date or task created date"] = None,
    task_status: Annotated[Optional[str], "Must be: open, in_progress, or closed"] = None,
    task_priority: Annotated[Optional[str], "Must be: veryLow, low, normal, high, veryHigh"] = None,    
    estimate_duration_minutes: Annotated[Optional[int], ""] = None,
    parent_project_name: Annotated[Optional[str], ""] = None,
    author_user_name: Annotated[Optional[str], ""] = None,
    assigned_user_names: Annotated[Optional[list[str]], ""] = None,
) -> str:
    """Find tasks"""
    response = AiInfoRequestModel(
        info_request_type=AiInfoRequestType.FIND_TASKS,
        args={
            "task_name": task_name,
            "task_description": task_description,
            "task_due_date": task_due_date,            
            "task_status": task_status,
            "task_priority": task_priority,
            "estimate_duration_minutes": estimate_duration_minutes,
            "parent_project_name": parent_project_name,
            "author_user_name": author_user_name,
            "assigned_user_names": assigned_user_names,
            "task_created_date": task_created_date,
            "date_search_radius_days": date_search_radius_days,
        }
    )
    return json.dumps(response.to_dict())

@tool 
def update_task_fields(
    task_name: Annotated[str, ""],
    task_description: Annotated[Optional[str], ""] = None,
    task_due_date: Annotated[Optional[str], "Must be in ISO 8601 format"] = None,
    task_status: Annotated[Optional[str], "Must be: open, in_progress, or closed"] = None,
    task_priority: Annotated[Optional[str], "Must be: veryLow, low, normal, high, veryHigh"] = None,    
    estimate_duration_minutes: Annotated[Optional[int], ""] = None,
) -> str:
    """Update fields of a task"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.UPDATE_TASK_FIELDS,
        args={
            "task_name": task_name,
            "task_description": task_description,
            "task_due_date": task_due_date,
            "task_status": task_status,
            "task_priority": task_priority,
            "estimate_duration_minutes": estimate_duration_minutes,
        }
    )
    return json.dumps(response.to_dict())

@tool
def delete_task(
    task_name: Annotated[str, ""]
) -> str:
    """Delete a task"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.DELETE_TASK,
        args={"task_name": task_name}
    )
    return json.dumps(response.to_dict())

@tool
def assign_user_to_task(
    task_name: Annotated[str, ""],
    user_name: Annotated[str, ""],
) -> str:
    """Assign a user to a task"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.ASSIGN_USER_TO_TASK,
        args={"task_name": task_name, "user_name": user_name}
    )
    return json.dumps(response.to_dict())


def get_tools():
    return [create_task, find_tasks, update_task_fields, delete_task]

def get_ai_request_tools():
    return [find_tasks]