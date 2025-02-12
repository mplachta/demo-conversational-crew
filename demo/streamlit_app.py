import streamlit as st
import requests
import time
import json

base_url = st.secrets["base_url"]
bearer_token = st.secrets["bearer_token"]
headers = {"Authorization": f"Bearer {bearer_token}"}
crewai_conversation_id = None

def poll_status(kickoff_id):
    global crewai_conversation_id
    max_polling_time = 30 # seconds

    while max_polling_time > 0: 
        status_response = requests.get(f"{base_url}/status/{kickoff_id}", headers=headers)
        if status_response.ok:
            status_data = status_response.json()
            if status_data["state"] == "SUCCESS":
                result = json.loads(status_data["result"])
                response = result["response"]
                st.chat_message("assistant").markdown(response)
                
                crewai_conversation_id = result["id"]
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

    if crewai_conversation_id is not None:
        inputs["id"] = crewai_conversation_id
    
    
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

st.set_page_config(
    page_title="CrewAI Conversational Agents Demo",
    page_icon="💬",
    layout="wide"
)

st.title('CrewAI Conversational Agents Demo')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(placeholder="Your message..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner(text="Thinking..."):
        response = submit_message(prompt)
    
        st.session_state.messages.append({"role": "assistant", "content": response})

