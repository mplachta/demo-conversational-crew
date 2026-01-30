import os
import logging
import requests
import time
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

base_url = os.environ.get("CREWAI_BASE_URL")
bearer_token = os.environ.get("CREWAI_BEARER_TOKEN")
headers = {"Authorization": f"Bearer {bearer_token}"}

conversation_sessions = {}
active_threads = set()


def get_session_id(channel_id: str, thread_ts: str = None) -> str:
    """Generate a unique session ID for the conversation."""
    if thread_ts:
        return f"{channel_id}_{thread_ts}"
    return channel_id


def poll_status(kickoff_id, max_polling_time=60):
    """Poll the API for the status of a kickoff request."""
    while max_polling_time > 0:
        try:
            status_response = requests.get(
                f"{base_url}/status/{kickoff_id}",
                headers=headers,
                timeout=5
            )
            
            if status_response.ok:
                status_data = status_response.json()
                if status_data["state"] == "SUCCESS":
                    result = json.loads(status_data["result"])
                    return result
                elif status_data["state"] == "FAILURE":
                    logger.error(f"Kickoff failed: {status_data.get('error', 'Unknown error')}")
                    return None
            else:
                logger.error(f"Status check failed: {status_response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during polling: {str(e)}")
            return None
            
        time.sleep(1)
        max_polling_time -= 1
    
    logger.error("Timeout: The agent did not complete the conversation within the allowed time.")
    return None


def submit_message(message, session_id=None):
    """Submit a message to the CrewAI API and poll for the response."""
    inputs = {"current_message": message}
    
    if session_id:
        inputs["id"] = session_id
    
    try:
        response = requests.post(
            f"{base_url}/kickoff",
            json={"inputs": inputs},
            headers=headers,
            timeout=10
        )
        
        if response.ok:
            kickoff_id = response.json().get("kickoff_id")
            if kickoff_id:
                return poll_status(kickoff_id)
            else:
                logger.error("No kickoff_id in response")
                return None
        else:
            logger.error(f"Kickoff request failed: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during message submission: {str(e)}")
        return None


@app.event("app_mention")
def handle_mention(event, say, client):
    """Handle when the bot is mentioned in a channel or thread."""
    try:
        user = event.get("user")
        text = event.get("text", "")
        channel = event.get("channel")
        thread_ts = event.get("thread_ts") or event.get("ts")
        
        bot_user_id = client.auth_test()["user_id"]
        message = text.replace(f"<@{bot_user_id}>", "").strip()
        
        if not message:
            session_id = get_session_id(channel, thread_ts)
            active_threads.add(session_id)
            say(
                text="Hi! How can I help you with Chase Freedom card benefits?",
                thread_ts=thread_ts
            )
            return
        
        session_id = get_session_id(channel, thread_ts)
        
        logger.info(f"Processing mention from user {user} in channel {channel}: '{message}'")
        
        crewai_session_id = conversation_sessions.get(session_id)
        
        result = submit_message(message, crewai_session_id)
        
        if result:
            conversation_sessions[session_id] = result["id"]
            active_threads.add(session_id)
            
            say(
                text=result["response"],
                thread_ts=thread_ts
            )
            
            logger.info(f"Sent response to thread {thread_ts}: '{result['response'][:100]}...'")
        else:
            say(
                text="Sorry, I encountered an error processing your request. Please try again.",
                thread_ts=thread_ts
            )
            logger.error(f"Failed to get response for message: {message}")
        
    except Exception as e:
        logger.error(f"Error handling mention: {str(e)}", exc_info=True)
        say(
            text="Sorry, I encountered an error processing your request. Please try again.",
            thread_ts=event.get("thread_ts") or event.get("ts")
        )


@app.event("assistant_thread_started")
def handle_assistant_thread_started(event, say, client, logger):
    """Handle when a user starts a thread with the assistant."""
    try:
        channel = event.get("assistant_thread", {}).get("channel_id")
        thread_ts = event.get("assistant_thread", {}).get("thread_ts")
        user = event.get("assistant_thread", {}).get("user_id")
        
        if not channel or not thread_ts:
            logger.warning("Missing channel or thread_ts in assistant_thread_started event")
            return
        
        session_id = get_session_id(channel, thread_ts)
        active_threads.add(session_id)
        
        logger.info(f"Assistant thread started by user {user} in channel {channel}, thread {thread_ts}")
        
        say(
            text="Hi! I'm here to help you with Chase Freedom card benefits. What would you like to know?",
            thread_ts=thread_ts,
            channel=channel
        )
        
    except Exception as e:
        logger.error(f"Error handling assistant_thread_started: {str(e)}", exc_info=True)


@app.event("assistant_thread_context_changed")
def handle_assistant_thread_context_changed(event, logger):
    """Handle when the context of an assistant thread changes."""
    try:
        channel = event.get("assistant_thread", {}).get("channel_id")
        thread_ts = event.get("assistant_thread", {}).get("thread_ts")
        
        if not channel or not thread_ts:
            logger.debug("Missing channel or thread_ts in assistant_thread_context_changed event")
            return
        
        session_id = get_session_id(channel, thread_ts)
        active_threads.add(session_id)
        
        logger.debug(f"Assistant thread context changed in channel {channel}, thread {thread_ts}")
        
    except Exception as e:
        logger.error(f"Error handling assistant_thread_context_changed: {str(e)}", exc_info=True)


@app.event("message")
def handle_message_events(event, say, client, logger):
    """Handle message events in threads where bot is active and direct messages."""
    try:
        # Debug: Log all incoming message events
        logger.debug(f"Received message event: channel={event.get('channel')}, thread_ts={event.get('thread_ts')}, channel_type={event.get('channel_type')}, subtype={event.get('subtype')}, text={event.get('text', '')[:50]}")
        
        if event.get("subtype") is not None:
            return
        
        bot_user_id = client.auth_test()["user_id"]
        if event.get("user") == bot_user_id:
            return
        
        text = event.get("text", "").strip()
        if not text:
            return
        
        channel = event.get("channel")
        channel_type = event.get("channel_type")
        thread_ts = event.get("thread_ts")
        user = event.get("user")
        
        # Handle direct messages (DMs)
        if channel_type == "im":
            session_id = get_session_id(channel, None)
            logger.info(f"Processing DM from user {user}: '{text}'")
            
            crewai_session_id = conversation_sessions.get(session_id)
            result = submit_message(text, crewai_session_id)
            
            if result:
                conversation_sessions[session_id] = result["id"]
                say(text=result["response"])
                logger.info(f"Sent DM response to user {user}: '{result['response'][:100]}...'")
            else:
                say(text="Sorry, I encountered an error processing your request. Please try again.")
                logger.error(f"Failed to get response for DM: {text}")
            return
        
        # Handle thread messages in channels
        if not thread_ts:
            logger.debug(f"No thread_ts, ignoring message in channel {channel}")
            return
        
        session_id = get_session_id(channel, thread_ts)
        
        logger.debug(f"Checking if session_id {session_id} is in active_threads: {session_id in active_threads}. Active threads: {active_threads}")
        
        if session_id not in active_threads:
            logger.debug(f"Session {session_id} not in active threads, ignoring message")
            return
        
        logger.info(f"Processing thread message from user {user} in channel {channel}: '{text}'")
        
        crewai_session_id = conversation_sessions.get(session_id)
        result = submit_message(text, crewai_session_id)
        
        if result:
            conversation_sessions[session_id] = result["id"]
            
            say(
                text=result["response"],
                thread_ts=thread_ts
            )
            
            logger.info(f"Sent thread response to {thread_ts}: '{result['response'][:100]}...'")
        else:
            say(
                text="Sorry, I encountered an error processing your request. Please try again.",
                thread_ts=thread_ts
            )
            logger.error(f"Failed to get response for message: {text}")
            
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}", exc_info=True)


def main():
    """Start the Slack bot using Socket Mode."""
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    logger.info("⚡️ Slack bot is running!")
    handler.start()


if __name__ == "__main__":
    main()
