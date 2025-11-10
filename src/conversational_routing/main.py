#!/usr/bin/env python
from pydantic import BaseModel
from typing import List
import json

from crewai.flow import Flow, listen, start, persist

from conversational_routing.crews.assistant_crew.assistant_crew import AssistantCrew

class ChatState(BaseModel):
    # id : str is a hidden Flow state property maintained by CrewAI framework
    current_message: str = ""
    conversation_history: List[dict] = []

# Here's how @persist() works:
# * if inputs['id'] is provided, CrewAI will use it to resume the conversation (retrieve the state from database)
# * if inputs['id'] is not provided, CrewAI will create a new conversation (persist the state to database)
@persist()
class ChatFlow(Flow[ChatState]):
    @start()
    def filter_messages(self):
        # Use this method to filter messages, clean them up, limit context, etc.
        pass
    
    @listen(filter_messages)
    def answer_message(self):
        # Call the crew that will respond to the user message
        assistant_crew = AssistantCrew().crew().kickoff({
            "current_message": self.state.current_message,
            "conversation_history": self.state.conversation_history
        })

        response = assistant_crew.raw

        # Update the conversation history in context
        self.state.conversation_history.append({"role": "user", "content": self.state.current_message})
        self.state.conversation_history.append({"role": "assistant", "content": response})

        # Return the response and conversation ID
        return json.dumps({
            "response": response,
            "id": self.state.id
        })
    
def kickoff():
    chat_flow = ChatFlow()
    chat_flow.kickoff(inputs={})

def plot():
    chat_flow = ChatFlow()
    chat_flow.plot()

if __name__ == "__main__":
    kickoff()
