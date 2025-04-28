#!/usr/bin/env python
from pydantic import BaseModel
from typing import List
import json

from crewai.flow import Flow, start, persist

from src.conversational_routing.crews.assistant_crew.assistant_crew import AssistantCrew

class ChatState(BaseModel):
    current_message: str = ""
    conversation_history: List[dict] = []

@persist()
class ChatFlow(Flow[ChatState]):
    @start()
    def answer_message(self):
        # Here define the crew that will respond to the user message
        assistant_crew = AssistantCrew().crew().kickoff({
            "current_message": self.state.current_message,
            "conversation_history": self.state.conversation_history
        })

        response = assistant_crew.raw

        self.state.conversation_history.append({"role": "user", "content": self.state.current_message})
        self.state.conversation_history.append({"role": "assistant", "content": response})

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
