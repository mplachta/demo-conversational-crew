import time

from colorama import Fore, Style

from src.conversational_routing.main import ChatFlow

messages = [
    "Hello",
    "Tell me about benefits",
    "Is there an extended warranty protection?",
    "What are coverage limits?",
]

session_id = None

for i, message in enumerate(messages):
    print(f"\n{Fore.BLUE}{Style.BRIGHT}Question #{i + 1}{Style.RESET_ALL}")

    chat_flow = ChatFlow()
    inputs = {"current_message": message}

    if session_id is not None:
        inputs["id"] = session_id

    response = chat_flow.kickoff(inputs=inputs)

    print(f"{Style.BRIGHT}Response:{Style.RESET_ALL} ", response)
    print(f"{Style.DIM}{chat_flow.state}{Style.RESET_ALL}")

    session_id = chat_flow.state.id
    time.sleep(5)
