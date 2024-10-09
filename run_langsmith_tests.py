from langsmith import Client
from langsmith.schemas import Run, Example
from langsmith.evaluation import evaluate
import json

from agent import State, run_ai_with_messages


# === Read in Langsmith Dataset Examples ===
client = Client()

dataset_name = "initial-test"
examples = client.list_examples(dataset_name=dataset_name)

# === Define AI system wrapper ===
def predict(inputs: dict) -> dict:
    messages = inputs["messages"]
    return State(messages=run_ai_with_messages(messages))

# === Define Evaluators === 
def test_evaluator(run: Run, example: Example) -> dict:

    # Ref output is in Langsmith dictionary Format 
    ref_output = example.outputs.get("messages")

    # Cur output is in BaseMessage Format 
    cur_output = run.outputs.get("messages")

    # Pretty print the reference and current output in JSON format
    #print("Reference Output:", json.dumps(ref_output, indent=4))

    # Breaks - BaseMessage is not JSON serializable    
    # TODO - figure out output format 
    print("Current Output:", cur_output)

    return {"key": "test_evaluator","score": 1.0}

# === Run Evaluation === 
experiment_results = evaluate(
    predict, # Your AI system
    data=dataset_name, # The data to predict and grade over
    evaluators=[test_evaluator], # The evaluators to score the results
    experiment_prefix="test",
    metadata={
        "version": "0.0.1",
    },
)

