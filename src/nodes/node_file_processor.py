from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from src.agent_state import AgentState
from src.llm_config import file_processor_llm_with_tools

def node_file_retriever(state: AgentState, config: RunnableConfig):
    """First node that focuses only on retrieving the file content."""
    # Get the current messages
    messages = state.get("messages", [])
    
    # Add system message with file retrieval instructions - making it much clearer
    system_message = """You are an AI assistant that ONLY retrieves files from storage.

    IMPORTANT INSTRUCTIONS - READ CAREFULLY:
    
    1. Your ONLY task right now is to use the get_supabase_file_content tool to retrieve a file.
    
    2. You MUST ONLY call the get_supabase_file_content tool with the bucket_name and file_path from the user's message.
    
    3. DO NOT call any other tools - those will be used in a later step.
    
    4. DO NOT try to analyze the file content or create tasks yet.
    
    5. After retrieving the file, respond ONLY with the file content.
    
    6. DO NOT call multiple tools - ONLY call the get_supabase_file_content tool.
    
    Remember: In this step, you are ONLY retrieving the file. Task creation will happen in a separate step later.
    """
    
    retrieval_messages = [SystemMessage(content=system_message)] + messages
    
    # print(f"File retriever sending messages to LLM: {retrieval_messages}")
    
    response = file_processor_llm_with_tools.invoke(retrieval_messages)
    
    # print(f"File retriever received response from LLM: {response}")

    result = {
        "messages": messages + [response]
    }
    
    # print(f"File retriever returning result: {result}")
    # Return updated state with the response
    return result

def node_task_creator(state: AgentState, config: RunnableConfig):
    """Second node that focuses on creating tasks based on the retrieved file."""
    # Get the current messages
    messages = state.get("messages", [])

    print(f"Task creator received messages: {messages}")
    
    # Find the file content from the previous tool message
    file_content = None
    for i in range(len(messages)-1, -1, -1):
        if isinstance(messages[i], ToolMessage) and str(messages[i].name)=="get_supabase_file_content":
            file_content = messages[i].content
            break

    print(f"File content: {file_content}")
    
    if not file_content:
        print("No file content found in the conversation history. Please retrieve the file first.")
        # If no file content found, return an error
        return {
            "messages": messages + [AIMessage(content="Error: No file content found in the conversation history. Please retrieve the file first.")],
            "next_node": "END"  # Signal to end the process
        }
    
    # Add system message with task creation instructions
    system_message = """You are an AI assistant that creates tasks based on file content.

    The file has already been retrieved. Now your job is to:
    
    1. ANALYZE the file content thoroughly to understand its structure and information.
    
    2. CREATE MULTIPLE TASKS using the create_task tool:
       - Create logical, well-organized tasks based on the file content
       - Each task should have a clear name and description
       - Use parent_project_id from the user's message to associate tasks with the project
       - Set appropriate priorities and due dates if you can determine them
       - Break down complex items into multiple tasks when appropriate
    
    3. When all tasks have been created, provide a brief summary of what you did.
    
    IMPORTANT: 
    - Make sure each task you create is directly related to the content of the file. Do not create generic tasks.
    - You can call the create_task tool multiple times in parallel to create multiple tasks efficiently.

    Here's the file content:
    {file_content}
    """
    
    response = file_processor_llm_with_tools.invoke([SystemMessage(content=system_message)])
    
    print(f"Task creator received response from LLM: {response}")
    
    # Return updated state with the response
    return {
        "messages": messages + [response]
    }