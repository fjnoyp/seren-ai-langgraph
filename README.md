
# Getting Started 

If the poetry environment doesn't run, manually start via: 
`poetry shell` 




# Running LangGraph Cloud Locally 

Ref: https://langchain-ai.github.io/langgraph/cloud/quick_start/

1. Make sure Docker is running
2. In terminal run: `langgraph up`
3. The inputs must match the State type specified in the graph builder for example: 

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



# Considerations

- Restart the terminal whenever you update the .env file - otherwise old values will be used 

- The Langchain BaseMessage types are not the same as the key/value input/output examples from LangSmith. The same fields exist, but BaseMessage is a type while LangSmith provides dictionaries. 



"assistant_id": "26a81bcc-ba25-4d1a-88b9-f1cbd48b0765",
  "graph_id": "agent",

thread id: 
380835cd-1ce7-435c-b50a-f7f7b684dc30