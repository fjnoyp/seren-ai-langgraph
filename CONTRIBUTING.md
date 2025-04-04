# Contributing to Seren AI LangGraph

This document provides guidelines for setting up your development environment and contributing to the Seren AI LangGraph project.

## Development Environment Setup

### Poetry Environment

Set up your Poetry environment:

```bash
# Create and activate the virtual environment
poetry shell

# Install dependencies
poetry install
```

If the Poetry environment doesn't run automatically, manually start it via:
```bash
poetry shell
```

## Running LangGraph Cloud Locally

Reference: https://langchain-ai.github.io/langgraph/cloud/quick_start/

1. Make sure Docker is running
2. In terminal run: 
   ```bash
   langgraph up
   ```
3. The inputs must match the State type specified in the graph builder. For example:

```json 
[
  {
    "role": "human",
    "content": "Alright what are you capable of?"
  }
]
```

### Local Deployment URLs
- API: http://localhost:8123
- Docs: http://localhost:8123/docs
- Debugger: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123

## Production Deployment

The project is configured for automatic deployment to LangGraph Cloud:

1. Push your changes to GitHub
2. LangGraph Cloud will automatically deploy the latest version

## Important Considerations

### Environment Variables

- LangGraph Cloud handles all memory management and checkpointing - unlike standard LangGraph installations
- Restart the terminal whenever you update the `.env` file - otherwise old values will be used

### Message Types

- The Langchain BaseMessage types are not the same as the key/value input/output examples from LangSmith
- The same fields exist, but BaseMessage is a type while LangSmith provides dictionaries
## Testing

When testing, ensure your input matches the expected state structure. The LangGraph API expects a properly formatted message array.

## Debugging Tips

1. Use the LangSmith debugger (https://smith.langchain.com/) to inspect the execution flow
2. Check the local API docs for endpoint specifications
3. Verify Docker is running correctly if you have issues with the local deployment

## Pull Request Process

1. Ensure your code follows the project's style guidelines
2. Update documentation as needed
3. Make sure all tests pass locally
4. Submit your pull request with a clear description of the changes 