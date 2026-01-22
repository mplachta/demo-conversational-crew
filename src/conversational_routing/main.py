#!/usr/bin/env python
from pydantic import BaseModel
from typing import List
import json

from crewai.flow import Flow, listen, start, persist, router, or_
from crewai import Agent

from conversational_routing.crews.assistant_crew.assistant_crew import AssistantCrew

class ChatState(BaseModel):
    # id : str is a hidden Flow state property maintained by CrewAI framework
    current_message: str = ""
    conversation_history: List[dict] = []
    
    current_agent: str = ""
    current_agent_response: str = ""
    
    classification: str = ""
    

# Here's how @persist() works:
# * if inputs['id'] is provided, CrewAI will use it to resume the conversation (retrieve the state from database)
# * if inputs['id'] is not provided, CrewAI will create a new conversation (persist the state to database)
@persist()
class ChatFlow(Flow[ChatState]):
    @start()
    def initial_processing(self):
        pass
    
    @router(initial_processing)
    def classify_message(self):
        classification_agent = Agent(
            role="User Prompt Classification Agent",
            goal="Classify the user prompt into one of the following categories: pleasantries, question, or non-Chase question.",
            backstory=("You are a user prompt classification agent. "
                       "You understand if the user is just sending a pleasantry or a general conversation item - then return 'pleasantries'. "
                       "If the user is asking a question related to Chase Freedom card benefits such as Auto Rental Coverage, Extended Warranty Protection, Purchase Protection, Roadside Assistance, Travel and Emergency Assistance, Trip Cancellation and Interruption Insurance - then return 'question'. "
                       "If the user is asking a question that is not related to Chase Freedom card benefits - then return 'non-chase-question'."),
            verbose=False,
        )
        
        classification_task = (
            f"Evaluate the user prompt: '{self.state.current_message}'.\n\n"
            f"Consider Conversation History:\n{self.state.conversation_history}.\n\n"
            "Return the classification result as a single word: pleasantries, question, or non-chase-question."
        )
        
        result = classification_agent.kickoff(classification_task)
        
        self.state.classification = result.raw
        
        if self.state.classification == "pleasantries":
            return "respond_to_pleasantries"
        elif self.state.classification == "question":
            return "respond_to_question"
        elif self.state.classification == "non-chase-question":
            return "respond_to_non_chase_question"
    
    @listen("respond_to_pleasantries")
    def answer_pleasantries(self):
        simple_response_agent = Agent(
            role="Chase Freedom Card Assistant",
            goal="Respond to the user's pleasantry",
            backstory=(
                "You are a friendly Chase Freedom Benefits card assistant. "
                "You understand if the user is just sending a pleasantry or a general conversation item "
                "You respond to the user's pleasantry with a friendly, short message."),
            verbose=False,
        )
        
        self.state.current_agent_response = simple_response_agent.kickoff(f"Respond to the user's pleasantry: '{self.state.current_message}'.").raw
        self.state.current_agent = "simple_response_agent"
        
    @listen("respond_to_question")
    def answer_question(self):
        # Call the crew that will respond to the user message
        assistant_crew = AssistantCrew().crew().kickoff({
            "current_message": self.state.current_message,
            "conversation_history": self.state.conversation_history
        })

        self.state.current_agent_response = assistant_crew.raw
        self.state.current_agent = "chase_question_crew"
        
    @listen("respond_to_non_chase_question")
    def answer_non_chase_question(self):
        self.state.current_agent_response = "This doesn't look like a Chase Freedom card question, can you please try something else?"
        self.state.current_agent = "non_chase_question_crew"
        
    @listen(or_(answer_pleasantries, answer_question, answer_non_chase_question))
    def send_response(self):
        # Update the conversation history in context
        self.state.conversation_history.append({"role": "user", "content": self.state.current_message})
        self.state.conversation_history.append({"role": "assistant", "content": self.state.current_agent_response})

        # Return the response and conversation ID
        return json.dumps({
            "id": self.state.id,
            "response": self.state.current_agent_response,
            "current_agent": self.state.current_agent,
            "classification": self.state.classification
        })
        
    
def kickoff():
    chat_flow = ChatFlow()
    chat_flow.kickoff(inputs={})

def plot():
    chat_flow = ChatFlow()
    chat_flow.plot()

if __name__ == "__main__":
    kickoff()
