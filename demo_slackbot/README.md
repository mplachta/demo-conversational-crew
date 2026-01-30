# CrewAI Slack Bot

A Slack bot that integrates with CrewAI's conversational routing system to provide intelligent responses about Chase Freedom card benefits.

## Features

- **Thread Support**: Responds in threads to keep conversations organized
- **Mention-Based**: Activate the bot by mentioning it (@botname)
- **Session Management**: Maintains conversation context across messages in the same thread
- **CrewAI Integration**: Uses the conversational routing flow for intelligent responses

## Prerequisites

- Python 3.10+
- A Slack workspace where you have permission to install apps
- Access to a deployed CrewAI API endpoint with bearer token authentication

## Setup

### 1. Create a Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "CrewAI Assistant") and select your workspace
4. Click "Create App"

### 2. Configure Bot Permissions

1. Navigate to "OAuth & Permissions" in the sidebar
2. Under "Scopes" → "Bot Token Scopes", add:
   - `app_mentions:read` - View messages that directly mention the bot
   - `chat:write` - Send messages as the bot
   - `channels:history` - View messages in public channels
   - `groups:history` - View messages in private channels (if needed)
   - `im:history` - View messages in direct messages (if needed)
   - `mpim:history` - View messages in group direct messages (if needed)

### 3. Enable Socket Mode

1. Navigate to "Socket Mode" in the sidebar
2. Enable Socket Mode
3. Generate an App-Level Token with `connections:write` scope
4. Save this token (starts with `xapp-`)

### 4. Enable Event Subscriptions

1. Navigate to "Event Subscriptions" in the sidebar
2. Toggle "Enable Events" to On
3. Under "Subscribe to bot events", add:
   - `app_mention` - When the bot is mentioned
   - `assistant_thread_started` - When a user starts a thread with the assistant
   - `assistant_thread_context_changed` - When the context of an assistant thread changes
   - `message.channels` - Messages in channels
   - `message.groups` - Messages in private channels (optional)
   - `message.im` - Direct messages (optional)

### 5. Install the App to Your Workspace

1. Navigate to "Install App" in the sidebar
2. Click "Install to Workspace"
3. Authorize the app
4. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 6. Configure Environment Variables

1. Copy `.env.sample` to `.env`:
   ```bash
   cp .env.sample .env
   ```

2. Edit `.env` and add your tokens:
   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   SLACK_APP_TOKEN=xapp-your-app-token-here
   CREWAI_BASE_URL=https://your-crewai-api-url.com
   CREWAI_BEARER_TOKEN=your-bearer-token-here
   ```

   **Note**: Get your CrewAI API credentials from your CrewAI deployment or platform account.

### 7. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Bot

```bash
python app.py
```

You should see:
```
⚡️ Slack bot is running!
```

## Usage

1. **Direct Messages (DMs)**: Send a direct message to the bot
   ```
   User DMs bot: Hello
   Bot: [Response]
   User: Tell me about extended warranty protection
   Bot: [Response with full conversation context]
   ```

2. **Channel Mentions**: Mention the bot with your question in a channel
   ```
   @CrewAI Assistant Hello
   @CrewAI Assistant Tell me about extended warranty protection
   ```

3. **Assistant Thread**: If your Slack workspace has assistant threads enabled, users can start a thread with the bot directly
   ```
   [User clicks "Message Assistant" or starts assistant thread]
   └─ Bot: Hi! I'm here to help you with Chase Freedom card benefits. What would you like to know?
      └─ What are the benefits?  (no mention needed)
         └─ Bot: [Response about benefits]
   ```

4. **Thread Conversations**: Once you mention the bot in a thread or start an assistant thread, it will respond to all subsequent messages in that thread without requiring additional mentions
   ```
   @CrewAI Assistant What are the benefits?
   └─ Bot: [Response about benefits]
      └─ What are the coverage limits?  (no mention needed)
         └─ Bot: [Response with context from previous messages]
            └─ Tell me more  (no mention needed)
               └─ Bot: [Continues conversation with full context]
   ```

   **Note**: 
   - Direct messages maintain conversation context throughout the entire DM conversation
   - In channels, the bot only responds to threads where it has been explicitly mentioned or where an assistant thread was started

## How It Works

1. **Event Handling**: The bot listens for multiple Slack events using Socket Mode:
   - `app_mention` - When explicitly mentioned with @botname
   - `assistant_thread_started` - When a user starts an assistant thread
   - `assistant_thread_context_changed` - When assistant thread context updates (ensures thread stays active)
   - `message` - For direct messages and follow-up messages in active threads
2. **Session Management**: 
   - Each thread gets a unique session ID (channel_id + thread_ts)
   - Each DM conversation gets a unique session ID (channel_id)
   - Sessions maintain conversation context across messages
3. **API Request**: Messages are submitted to the CrewAI API via HTTP POST to `/kickoff` endpoint
4. **Polling**: The bot polls the `/status/{kickoff_id}` endpoint until the response is ready (max 60 seconds)
5. **Response**: The bot replies in the same thread/DM with the AI-generated response

## Architecture

```
User mentions bot in Slack
    ↓
Slack sends event to bot (Socket Mode)
    ↓
Bot extracts message and thread context
    ↓
HTTP POST to CrewAI API /kickoff endpoint
    ↓
Receive kickoff_id
    ↓
Poll /status/{kickoff_id} endpoint (every 1s, max 60s)
    ↓
CrewAI processes message and returns result
    ↓
Response sent back to Slack thread
```

## Troubleshooting

### Bot doesn't respond
- Check that the bot is running (`python app.py`)
- Verify Socket Mode is enabled
- Ensure the bot is invited to the channel (`/invite @botname`)
- Check logs for errors

### "Missing required scopes" error
- Review the OAuth scopes in your Slack app settings
- Reinstall the app to workspace after adding scopes

### Conversation context not maintained
- Verify that messages are in the same thread
- Check that `conversation_sessions` dictionary is persisting session IDs

## Development

To modify the bot behavior:
- Edit `app.py` to change event handling logic or polling parameters
- Modify the CrewAI flow on your deployed API endpoint
- Add new event handlers for different Slack events
- Adjust `max_polling_time` in `poll_status()` function if needed (default: 60 seconds)

## Security Notes

- Never commit `.env` file to version control
- Keep your Slack tokens secure
- Use environment variables for all sensitive data
- Consider implementing rate limiting for production use
