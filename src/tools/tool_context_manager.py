from contextlib import contextmanager
from contextvars import ContextVar

# Create context variables
tool_context = ContextVar('tool_context', default=None)

@contextmanager
def set_tool_context(config: dict):
    token = tool_context.set(config)
    try:
        yield
    finally:
        tool_context.reset(token)


# Example getting context: 
# context = tool_context.get()

# print(f'from shift_tools: {context}')

# print(f'from shift_tools: {context["user_id"]}')
# print(f'from shift_tools: {context["org_id"]}')

# """Get the current shift for a user"""
# return f"Current shift for user: {context['user_id']}"        