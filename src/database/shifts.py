from src.database.postgres_client import execute_query
from src.supabase.supabase_client import supabase_client

# Run: poetry run python -m src.database.shifts

def get_user_shifts(user_id: str):
    query = '''
      SELECT DISTINCT s.*
      FROM shifts s
      JOIN shift_user_assignments sua ON s.id = sua.shift_id
      WHERE sua.user_id = %(user_id)s
    '''
    return execute_query(query, {"user_id": user_id})

result = get_user_shifts("ed3bea9c-628a-4f16-a7f3-508f46da9eac")
print(result)