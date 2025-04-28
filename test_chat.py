from src.conversational_routing.main import ChatFlow
from colorama import Fore, Style

messages = [
    "What is an Agent?",
    "How to set up Azure OpenAI connection?"
]

# First chat message
print(f"{Fore.BLUE}{Style.BRIGHT}Question #1{Style.RESET_ALL}")

chat_flow = ChatFlow()
response = chat_flow.kickoff(inputs={
    "current_message": messages[0],
})

print(f"{Style.BRIGHT}Response:{Style.RESET_ALL} ", response)
print(f"{Style.DIM}{chat_flow.state}{Style.RESET_ALL}")

id = chat_flow.state.id

print(f"\n{Fore.BLUE}{Style.BRIGHT}Question #2{Style.RESET_ALL}")

chat_flow = ChatFlow()
response = chat_flow.kickoff(inputs={
    "current_message": messages[1],
    "id": id
})

print(f"{Style.BRIGHT}Response:{Style.RESET_ALL} ", response)
print(f"{Style.DIM}{chat_flow.state}{Style.RESET_ALL}")