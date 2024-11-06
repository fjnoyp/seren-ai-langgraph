from src.database.postgres_client import execute_query

# Run: poetry run python -m src.database.test_postgres_client

result = execute_query("SELECT * FROM shifts")
print(result)