import os
from typing import Optional, Dict, Any
from supabase import Client

from src.supabase.supabase_client import supabase_client


async def get_note_description_by_id(note_id: str) -> Optional[str]:
    """
    Retrieves the description of a note by its ID from Supabase.

    Args:
        note_id: The ID of the note to retrieve

    Returns:
        The description of the note if found, None otherwise
    """
    try:
        response = (
            await supabase_client.table("notes")
            .select("description")
            .eq("id", note_id)
            .execute()
        )

        if response.data and len(response.data) > 0:
            return response.data[0].get("description")
        return None
    except Exception as e:
        print(f"Error retrieving note description: {e}")
        return None
