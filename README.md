
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



# Considerations

- Restart the terminal whenever you update the .env file - otherwise old values will be used 

- The Langchain BaseMessage types are not the same as the key/value input/output examples from LangSmith. The same fields exist, but BaseMessage is a type while LangSmith provides dictionaries. 