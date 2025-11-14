from src.conversational_routing.main import ChatFlow
from colorama import Fore, Style

messages = [
    "Is there an extended warranty protection?",
    "What are coverage limits?"
]

# First chat message
print(f"{Fore.BLUE}{Style.BRIGHT}Question #1{Style.RESET_ALL}")

chat_flow = ChatFlow()
response = chat_flow.kickoff(inputs={
    "current_message": messages[0],
})

print(f"{Style.BRIGHT}Response:{Style.RESET_ALL} ", response)
print(f"{Style.DIM}{chat_flow.state}{Style.RESET_ALL}")

session_id = chat_flow.state.id

print(f"\n{Fore.BLUE}{Style.BRIGHT}Question #2{Style.RESET_ALL}")

chat_flow = ChatFlow()
response = chat_flow.kickoff(inputs={
    "current_message": messages[1],
    "id": session_id
})

print(f"{Style.BRIGHT}Response:{Style.RESET_ALL} ", response)
print(f"{Style.DIM}{chat_flow.state}{Style.RESET_ALL}")