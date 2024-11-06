import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Run: poetry run python -m src.local.test_supabase

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

print("url", url)
print("key", key)

supabase_client: Client = create_client(url, key)