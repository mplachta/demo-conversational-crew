import json
import logging
import os
import time

import requests
from dotenv import load_dotenv
from slack_bolt import App, Assistant
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.context.get_thread_context import GetThreadContext
from slack_bolt.context.say import Say
from slack_bolt.context.set_status import SetStatus
from slack_bolt.context.set_suggested_prompts import SetSuggestedPrompts
from slack_bolt.context.set_title import SetTitle

load_dotenv()

log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
assistant = Assistant()

base_url = os.environ.get("CREWAI_BASE_URL")
bearer_token = os.environ.get("CREWAI_BEARER_TOKEN")
headers = {"Authorization": f"Bearer {bearer_token}"}

conversation_sessions = {}
conversation_histories = {}


def to_mrkdwn(text: str) -> str:
    """Convert standard markdown to Slack mrkdwn format."""
    import re

    # Bold: **text** or __text__ -> *text*
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)
    text = re.sub(r"__(.+?)__", r"*\1*", text)
    # Bullet points: - or * at line start -> • (before italic to avoid * conflict)
    text = re.sub(r"^\s*[-*]\s+", "• ", text, flags=re.MULTILINE)
    # Italic: *text* or _text_ (avoid converting already-converted bold)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"_\1_", text)
    # Headers: # H1, ## H2, etc. -> *bold*
    text = re.sub(r"^#{1,6}\s+(.+)$", r"*\1*", text, flags=re.MULTILINE)
    # Strikethrough: ~~text~~ -> ~text~
    text = re.sub(r"~~(.+?)~~", r"~\1~", text)
    return text


LOADING_MESSAGES = [
    "Reviewing your Chase Freedom benefits...",
    "Looking that up for you...",
    "Almost there...",
]


def set_channel_status(client, channel: str, thread_ts: str, status: str = ""):
    """Set or clear the assistant status for a channel thread."""
    try:
        client.assistant_threads_setStatus(
            channel_id=channel,
            thread_ts=thread_ts,
            status=status,
        )
    except Exception as e:
        logger.debug(f"Could not set channel status: {e}")


def make_blocks(response: str) -> list:
    """Wrap a response in a mrkdwn section block."""
    return [
        {"type": "section", "text": {"type": "mrkdwn", "text": to_mrkdwn(response)}}
    ]


SUGGESTED_PROMPTS = [
    {
        "title": "What benefits does Chase Freedom offer?",
        "message": "What benefits does the Chase Freedom card offer?",
    },
    {
        "title": "How do I earn cash back?",
        "message": "How do I earn cash back with my Chase Freedom card?",
    },
    {
        "title": "What's the sign-up bonus?",
        "message": "What is the sign-up bonus for the Chase Freedom card?",
    },
    {
        "title": "Are there any annual fees?",
        "message": "Does the Chase Freedom card have an annual fee?",
    },
]


def poll_status(kickoff_id, max_polling_time=60):
    """Poll the API for the status of a kickoff request."""
    while max_polling_time > 0:
        try:
            url = f"{base_url}/status/{kickoff_id}"
            logger.debug(f"[API REQUEST] GET {url}")
            status_response = requests.get(url, headers=headers, timeout=5)
            logger.debug(
                f"[API RESPONSE] GET {url} -> {status_response.status_code}: {status_response.text[:200]}"
            )

            if status_response.ok:
                status_data = status_response.json()
                if status_data["state"] == "SUCCESS":
                    result = json.loads(status_data["result"])
                    return result
                elif status_data["state"] == "FAILURE":
                    logger.error(
                        f"Kickoff failed: {status_data.get('error', 'Unknown error')}"
                    )
                    return None
            else:
                logger.error(f"Status check failed: {status_response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during polling: {str(e)}")
            return None

        time.sleep(1)
        max_polling_time -= 1

    logger.error(
        "Timeout: The agent did not complete the conversation within the allowed time."
    )
    return None


def submit_message(message, session_id=None, conversation_history=None):
    """Submit a message to the CrewAI API and poll for the response."""
    inputs = {"current_message": message}

    # if session_id:
    # inputs["id"] = session_id

    if conversation_history:
        inputs["conversation_history"] = conversation_history

    try:
        url = f"{base_url}/kickoff"
        body = {"inputs": inputs}
        logger.debug(f"[API REQUEST] POST {url} body={json.dumps(body)}")
        response = requests.post(url, json=body, headers=headers, timeout=10)
        logger.debug(
            f"[API RESPONSE] POST {url} -> {response.status_code}: {response.text[:200]}"
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


@assistant.thread_started
def handle_assistant_thread_started(
    payload: dict,
    say: Say,
    set_suggested_prompts: SetSuggestedPrompts,
    get_thread_context: GetThreadContext,
    logger: logging.Logger,
):
    """Welcome the user and present suggested prompts."""
    try:
        logger.debug(
            f"[SLACK EVENT] assistant_thread_started payload={json.dumps(payload)}"
        )
        say(
            "Hi! I'm here to help you with Chase Freedom card benefits. What would you like to know?"
        )
        set_suggested_prompts(prompts=SUGGESTED_PROMPTS)
    except Exception as e:
        logger.exception(f"Failed to handle assistant_thread_started: {e}")
        say(f":warning: Something went wrong! ({e})")


@assistant.user_message
def handle_user_message(
    payload: dict,
    say: Say,
    set_status: SetStatus,
    set_title: SetTitle,
    logger: logging.Logger,
):
    """Handle messages sent to the assistant thread."""
    try:
        logger.debug(f"[SLACK EVENT] user_message payload={json.dumps(payload)}")
        channel_id = payload["channel"]
        thread_ts = payload["thread_ts"]
        user_message = payload["text"]

        set_status(
            status="thinking...",
            loading_messages=[
                "Reviewing your Chase Freedom benefits...",
                "Looking that up for you...",
                "Almost there...",
            ],
        )

        session_key = f"{channel_id}_{thread_ts}"
        crewai_session_id = conversation_sessions.get(session_key)
        history = conversation_histories.get(session_key, [])

        result = submit_message(user_message, crewai_session_id, history)

        if result:
            conversation_sessions[session_key] = result["id"]
            history.append({"role": "user", "message": user_message})
            history.append({"role": "assistant", "message": result["response"]})
            conversation_histories[session_key] = history
            set_title(title=user_message[:50])
            say(text=result["response"], blocks=make_blocks(result["response"]))
        else:
            say(
                text=":warning: Sorry, I encountered an error processing your request. Please try again."
            )
            logger.error(f"Failed to get response for message: {user_message}")

    except Exception as e:
        logger.exception(f"Failed to handle user message: {e}")
        say(f":warning: Something went wrong! ({e})")


app.use(assistant)


@app.event("message")
def handle_thread_replies(event, say, client, logger):
    """Respond to follow-up messages in threads where the bot was already mentioned."""
    if event.get("subtype") is not None:
        return

    bot_user_id = client.auth_test()["user_id"]
    if event.get("user") == bot_user_id:
        return

    channel = event.get("channel")
    thread_ts = event.get("thread_ts")
    channel_type = event.get("channel_type")

    # Only handle channel thread replies, not DMs (those go through assistant thread)
    if channel_type == "im" or not thread_ts:
        return

    session_key = f"{channel}_{thread_ts}"

    # Only respond if this thread already has an active session from a prior mention
    if session_key not in conversation_sessions:
        return

    text = event.get("text", "").strip()
    if not text:
        return

    logger.debug(f"[SLACK EVENT] thread_reply event={json.dumps(event)}")

    set_channel_status(client, channel, thread_ts, "thinking...")

    crewai_session_id = conversation_sessions.get(session_key)
    history = conversation_histories.get(session_key, [])

    result = submit_message(text, crewai_session_id, history)
    set_channel_status(client, channel, thread_ts)

    if result:
        conversation_sessions[session_key] = result["id"]
        history.append({"role": "user", "message": text})
        history.append({"role": "assistant", "message": result["response"]})
        conversation_histories[session_key] = history
        say(
            text=result["response"],
            blocks=make_blocks(result["response"]),
            thread_ts=thread_ts,
        )
    else:
        say(
            text=":warning: Sorry, I encountered an error processing your request. Please try again.",
            thread_ts=thread_ts,
        )


@app.event("app_mention")
def handle_mention(event, say, client):
    """Handle when the bot is mentioned in a channel or thread."""
    try:
        logger.debug(f"[SLACK EVENT] app_mention event={json.dumps(event)}")
        text = event.get("text", "")
        channel = event.get("channel")
        thread_ts = event.get("thread_ts") or event.get("ts")

        bot_user_id = client.auth_test()["user_id"]
        message = text.replace(f"<@{bot_user_id}>", "").strip()

        if not message:
            say(
                text="Hi! How can I help you with Chase Freedom card benefits?",
                thread_ts=thread_ts,
            )
            return

        session_key = f"{channel}_{thread_ts}"
        set_channel_status(client, channel, thread_ts, "thinking...")

        crewai_session_id = conversation_sessions.get(session_key)
        history = conversation_histories.get(session_key, [])

        result = submit_message(message, crewai_session_id, history)
        set_channel_status(client, channel, thread_ts)

        if result:
            conversation_sessions[session_key] = result["id"]
            history.append({"role": "user", "message": message})
            history.append({"role": "assistant", "message": result["response"]})
            conversation_histories[session_key] = history
            say(
                text=result["response"],
                blocks=make_blocks(result["response"]),
                thread_ts=thread_ts,
            )
        else:
            say(
                text=":warning: Sorry, I encountered an error processing your request. Please try again.",
                thread_ts=thread_ts,
            )

    except Exception as e:
        logger.error(f"Error handling mention: {str(e)}", exc_info=True)
        say(
            text=":warning: Sorry, I encountered an error processing your request. Please try again.",
            thread_ts=event.get("thread_ts") or event.get("ts"),
        )


def main():
    """Start the Slack bot using Socket Mode."""
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    logger.info("⚡️ Slack bot is running!")
    handler.start()


if __name__ == "__main__":
    main()
