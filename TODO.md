1. Only get last 3-5 messages of history - currently we get entire history and it overloads the input token limit 

1a. Determine in Supabase is calling the local LangGraph run and how to switch easily to hosted one as necessary 

2. Maybe switch to Anthropic to improve performance? 

3. Create the shift functions and start testing the ai responses to them 

4. Determine the expected ai inputs and outputs for shift management 

ie. Do we send the user's current UI context yet? Maybe we can skip for now. 

So we just trust ai to translate user request into shift methods - what are those shifts methods, how might the AI search for needed info, 
how might that be returned to the front end? How will user confirmations work - in the ToolMessage format? Is the user response a ToolMessagE? 