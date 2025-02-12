import streamlit as st
import requests
import time
import json

base_url = st.secrets["base_url"]
bearer_token = st.secrets["bearer_token"]
headers = {"Authorization": f"Bearer {bearer_token}"}

# initialize session state

if 'crewai_conversation_id' not in st.session_state:
    st.session_state['crewai_conversation_id'] = None

if "messages" not in st.session_state:
    st.session_state.messages = []

crew_favicon = "data:image/png;base64,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"

# define api methods

def poll_status(kickoff_id):
    max_polling_time = 30 # seconds

    while max_polling_time > 0: 
        status_response = requests.get(f"{base_url}/status/{kickoff_id}", headers=headers)
        if status_response.ok:
            status_data = status_response.json()
            if status_data["state"] == "SUCCESS":
                result = json.loads(status_data["result"])
                response = result["response"]
                st.chat_message("crew", avatar=crew_favicon).markdown(response)
                
                st.session_state.crewai_conversation_id = result["id"]
                return response
        else:
            st.error(f"Error: {status_response.text}")
        time.sleep(1)
        max_polling_time -= 1
    
    if max_polling_time == 0:
        st.error("Timeout: The agent did not complete the conversation within the allowed time.")

def submit_message(message):
    inputs = {
        "current_message": message,
    }

    if st.session_state.crewai_conversation_id is not None:
        inputs["id"] = st.session_state.crewai_conversation_id
    
    response = requests.post(
        f"{base_url}/kickoff",
        json={ "inputs": inputs },
        headers=headers
    )

    if response.ok:
        kickoff_id = response.json().get("kickoff_id", "N/A")
        response = poll_status(kickoff_id)
        return response
    else:
        st.error(f"Error: {response.text}") 

# render page

st.set_page_config(
    page_title="CrewAI Conversational Agents Demo",
    page_icon="💬",
    layout="wide"
)

st.logo("https://cdn.prod.website-files.com/66cf2bfc3ed15b02da0ca770/66d07240057721394308addd_Logo%20(1).svg", link="https://www.crewai.com/", size="large")

st.sidebar.title("CrewAI Conversational Agents Demo")

st.sidebar.markdown("""
This demo showcases the power of CrewAI's conversational agents. 
Experience AI-driven conversations that adapt to your inputs and 
provide intelligent responses. Try asking questions or discussing 
various topics to see how the agents interact and collaborate.

Get started by typing a message in the chat input below!

The Crew that is answering the questions is called "CrewAI Expert".
It can answer questions about the CrewAI framework, provide concise and 
accurate information, and guide you in its effective use. It is using RAG 
(Retrieval-Augmented Generation) configured with our 
[Knowledge](https://docs.crewai.com/concepts/knowledge).
""")

st.sidebar.link_button("Open a CrewAI platform account", "https://app.crewai.com/", type="primary")

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=(crew_favicon if message["role"] == "crewai" else None)):
        st.markdown(message["content"])

if prompt := st.chat_input(placeholder="Your message..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner(text="Thinking...", show_time=True):
        response = submit_message(prompt)
    
        st.session_state.messages.append({"role": "crewai", "content": response})
