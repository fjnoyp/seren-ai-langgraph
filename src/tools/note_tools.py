import json
from langchain_core.tools import tool
from typing import Annotated, Optional
from pydantic import BaseModel, Field

from src.supabase.supabase_note_methods import get_note_description_by_id
from src.tools.ai_request_models import (
    AiActionRequestModel,
    AiActionRequestType,
    AiInfoRequestModel,
    AiInfoRequestType,
)

from langchain_core.messages import (
    SystemMessage,
)

from src.llm_config import single_call_llm, llm


# === NOTE TOOLS ===


@tool
def create_note(
    note_name: Annotated[str, ""],
    note_description: Annotated[str, ""],
    show_to_user: Annotated[
        Optional[bool],
        "Controls UI visibility",
    ] = True,
) -> str:
    """Create a note"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.CREATE_NOTE,
        args={"note_name": note_name, "note_description": note_description},
        show_to_user=show_to_user,
    )
    return json.dumps(response.to_dict())


class NoteEditOperation(BaseModel):
    """A single edit operation for a note"""

    type: str = Field(description="Type of edit operation: 'keep', 'remove', or 'add'")
    text: str = Field(description="The text content for this operation")


# TODO p2 - issue is AI might call this before knowing what the note content is
# We might have to build checks into this that force ai to get note description before and a separate step to generate the note diffs
@tool
async def update_note_description(
    note_id: Annotated[str, ""],
    note_name: Annotated[str, ""],
    note_description_changes: Annotated[
        str,
        "A description of the desired changes to the note description to be executed by another AI step",
    ] = None,
    show_to_user: Annotated[
        Optional[bool],
        "Controls UI visibility",
    ] = True,
) -> str:
    """Update the description of a note"""

    # 1 ) get the note and load its description ow
    note_description = await get_note_description_by_id(note_id)

    # 2 ) prompt an ai to generate the note diffs
    system_content = f"""
    You are an expert at generating structured note modifications. 
    
    Given a previous note description and requested changes, generate a JSON array of edit operations.
    Each operation should contain:
    - "type": either "keep", "remove", or "add"
    - "text": the text content for this operation

    The combined sequence of operations should form the complete updated note.

    Example input:
    Previous note: "We were working on the project yesterday"
    Changes: "Change 'were working' to 'are working' and add 'and made good progress' at the end"

    Example output:
    [
        {"type": "keep", "text": "We "},
        {"type": "remove", "text": "were working"},
        {"type": "add", "text": "are working"},
        {"type": "keep", "text": " on the project yesterday"},
        {"type": "add", "text": " and made good progress"}
    ]

    Previous note description: {note_description}
    Changes to the note description: {note_description_changes}    
    
    Respond only with the JSON array of operations.
    """
    system_message = SystemMessage(content=system_content)

    # Use structured output to get edit operations
    structured_llm = llm.with_structured_output(list[NoteEditOperation])
    update_note_description_response = structured_llm.invoke(system_message)

    # Convert to JSON for response
    edit_operations_json = json.dumps(
        [op.model_dump() for op in update_note_description_response]
    )

    # 3 ) return the diffs for the client to show
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.UPDATE_NOTE,
        args={
            "note_name": note_name,
            "updated_note_description": edit_operations_json,
        },
        show_to_user=show_to_user,
    )
    return json.dumps(response.to_dict())


@tool
def find_notes(
    note_name: Annotated[Optional[str], ""] = None,
    note_created_date_start: Annotated[Optional[str], ""] = None,
    note_created_date_end: Annotated[Optional[str], ""] = None,
    note_updated_date_start: Annotated[Optional[str], ""] = None,
    note_updated_date_end: Annotated[Optional[str], ""] = None,
    show_to_user: Annotated[
        Optional[bool],
        "Controls UI visibility",
    ] = True,
) -> str:
    """Find note(s)"""
    response = AiInfoRequestModel(
        info_request_type=AiInfoRequestType.FIND_NOTES,
        args={
            "note_name": note_name,
            "note_created_date_start": note_created_date_start,
            "note_created_date_end": note_created_date_end,
            "note_updated_date_start": note_updated_date_start,
            "note_updated_date_end": note_updated_date_end,
        },
        show_to_user=show_to_user,
    )
    return json.dumps(response.to_dict())


@tool
def share_note(
    note_name: Annotated[str, ""],
) -> str:
    """Share a note"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.SHARE_NOTE,
        args={"note_name": note_name},
    )
    return json.dumps(response.to_dict())


@tool
def delete_note(
    note_name: Annotated[str, ""],
) -> str:
    """Delete a note"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.DELETE_NOTE,
        args={"note_name": note_name},
    )
    return json.dumps(response.to_dict())


@tool
def show_notes(
    note_name: Annotated[Optional[str], ""] = None,
) -> str:
    """Show note(s) to the user"""
    response = AiActionRequestModel(
        action_request_type=AiActionRequestType.SHOW_NOTES,
        args={"note_name": note_name},
    )
    return json.dumps(response.to_dict())


def get_tools():
    return [
        create_note,
        find_notes,
        share_note,
        delete_note,
        show_notes,
    ]


def get_ai_request_tools():
    return [
        create_note,
        find_notes,
        share_note,
        delete_note,
        show_notes,
    ]
