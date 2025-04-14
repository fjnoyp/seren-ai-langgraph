import os
import io
import pandas as pd
from typing import Optional, Dict, Any
from supabase import Client

from src.supabase.supabase_client import supabase_client


def get_file_tools():
    return [
        get_file_from_bucket,
        get_excel_file_as_string,
        get_csv_file_as_string,
        get_supabase_file_content,
    ]


async def get_file_from_bucket(bucket_name: str, file_path: str) -> Optional[bytes]:
    """
    Retrieves a file from a Supabase storage bucket.

    Args:
        bucket_name: The name of the bucket where the file is stored
        file_path: The path to the file within the bucket

    Returns:
        The file content as bytes if found, None otherwise
    """
    try:
        response = supabase_client.storage.from_(bucket_name).download(file_path)
        return response
    except Exception as e:
        print(f"Error retrieving file from bucket: {e}")
        return None


async def get_excel_file_as_string(bucket_name: str, file_path: str) -> Optional[str]:
    """
    Retrieves an Excel file from a Supabase storage bucket and converts it to a string.

    Args:
        bucket_name: The name of the bucket where the Excel file is stored
        file_path: The path to the Excel file within the bucket

    Returns:
        The Excel file content as a formatted string if found, None otherwise
    """
    try:
        file_content = await get_file_from_bucket(bucket_name, file_path)
        
        if file_content is None:
            return None
            
        # Read Excel file into pandas DataFrame
        excel_file = io.BytesIO(file_content)
        df = pd.read_excel(excel_file)
        
        # Convert DataFrame to string representation
        return df.to_string(index=False)
    except Exception as e:
        print(f"Error processing Excel file: {e}")
        return None


async def get_csv_file_as_string(bucket_name: str, file_path: str) -> Optional[str]:
    """
    Retrieves a CSV file from a Supabase storage bucket and converts it to a string.

    Args:
        bucket_name: The name of the bucket where the CSV file is stored
        file_path: The path to the CSV file within the bucket

    Returns:
        The CSV file content as a formatted string if found, None otherwise
    """
    try:
        file_content = await get_file_from_bucket(bucket_name, file_path)
        
        if file_content is None:
            return None
            
        # Read CSV file into pandas DataFrame
        csv_file = io.BytesIO(file_content)
        df = pd.read_csv(csv_file)
        
        # Convert DataFrame to string representation
        return df.to_string(index=False)
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return None


async def get_supabase_file_content(bucket_name: str, file_path: str) -> Optional[str]:
    """
    Retrieves and processes a file from Supabase storage bucket and returns its content as a string.
    
    This function handles different file types (Excel, CSV, text) from Supabase storage
    and returns their content in a readable string format.

    Args:
        bucket_name: The name of the Supabase storage bucket where the file is stored
        file_path: The path to the file within the Supabase bucket

    Returns:
        A string containing the file content or an error message
    """
    try:
        # Determine file type and get content as string
        file_extension = os.path.splitext(file_path)[1].lower()
        file_content = None
        
        if file_extension == '.xlsx' or file_extension == '.xls':
            file_content = await get_excel_file_as_string(bucket_name, file_path)
        elif file_extension == '.csv':
            file_content = await get_csv_file_as_string(bucket_name, file_path)
        else:
            # For other file types, get raw content
            raw_content = await get_file_from_bucket(bucket_name, file_path)
            if raw_content:
                file_content = raw_content.decode('utf-8', errors='replace')
        
        if not file_content:
            return f"Could not process file from Supabase storage: {file_path}"
        
        return f"{file_content}"
        
    except Exception as e:
        print(f"Error processing file from Supabase storage: {e}")
        return f"Error processing file from Supabase storage: {str(e)}"
