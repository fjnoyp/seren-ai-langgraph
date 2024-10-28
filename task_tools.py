from langchain_core.tools import tool
from typing import Annotated

# === TASK TOOLS ===
# Note: llama keeps hallucinating a "brave_search" tool that doesn't exist

# To view the schema: create_task.args_schema.schema()
@tool(return_direct=True)
def request_to_create_task(
    task_name: Annotated[str, ""],
) -> str:
    """Create a task"""
    return f"Requested to create task: {task_name}"


@tool
def find_task(task_name: Annotated[str, ""]) -> str:
    """Find a task"""
    return f"Found task: {task_name}"


@tool
def update_task_status(
    task_name: Annotated[str, ""],
    task_status: Annotated[str, "Must be: open, in_progress, or closed"],
) -> str:
    """Update a task status"""
    return f"Updated task: {task_name} with status: {task_status}"


@tool(return_direct=True)
def request_to_delete_task(task_name: Annotated[str, ""]) -> str:
    """Delete a task"""
    return f"Requested to delete task: {task_name}"

task_tools = [request_to_create_task, find_task, update_task_status, request_to_delete_task]
