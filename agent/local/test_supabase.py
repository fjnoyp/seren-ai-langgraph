import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

print("url", url)
print("key", key)

supabase: Client = create_client(url, key)

response = supabase.table("tasks").select("*").execute()

print(response)