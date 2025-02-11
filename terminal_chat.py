from src.conversational_routing.main import ChatFlow
from colorama import Fore, Style

# First chat message
print(f"{Fore.BLUE}{Style.BRIGHT}This is a terminal chat with CID crew.{Style.RESET_ALL} (type 'exit' to quit)")
id = None
while True:
    user_input = input("> ")
    if user_input == "exit":
        break

    chat_flow = ChatFlow()
    inputs = {
        "current_message": user_input,
    }
    if id is not None:
        inputs["id"] = id
    
    response = chat_flow.kickoff(inputs=inputs)

    print(f"{Style.BRIGHT}Response:{Style.RESET_ALL} ", response)
    print(f"{Style.DIM}{chat_flow.state}{Style.RESET_ALL}")

    id = chat_flow.state.id