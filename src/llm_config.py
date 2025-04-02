from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from src.tools.tools import get_all_tools

# Define LLMs
llm = ChatGroq(model="llama-3.3-70b-versatile")
# llm = ChatOpenAI(model="gpt-4o-mini") - way too slow
# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash") - importing the required dependnecy breaks the entire graph
single_call_llm = ChatGroq(model="llama-3.1-8b-instant")
llm_with_tools = llm.bind_tools(get_all_tools(), parallel_tool_calls=False)
