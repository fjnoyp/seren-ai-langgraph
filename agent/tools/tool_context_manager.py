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