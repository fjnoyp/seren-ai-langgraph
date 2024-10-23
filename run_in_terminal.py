
from agent import run_ai_with_custom_input, run_ai_with_user_input

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        results = run_ai_with_custom_input(user_input)
        print(results[-1].pretty_print())        
    except Exception as e:
        print("An exception occurred: ", e)
        # fallback if input() is not available
        # user_input = "What do you know about LangGraph?"
        # print("User: " + user_input)
        # results = run_ai_with_user_input(user_input)
        # print(results[-1].pretty_print())        
        break
