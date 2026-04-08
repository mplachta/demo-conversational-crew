# CrewAI Slack Bot

A Slack bot that integrates with CrewAI's conversational routing system to provide intelligent responses about Chase Freedom card benefits.

## Features

- **AI Agent Thread**: Native Slack AI assistant panel with suggested prompts, status indicators, and thread titles
- **Channel Mentions**: Mention the bot once in a channel thread — it responds to all follow-ups automatically
- **Private Channel Support**: Works in both public and private channels
- **Conversation History**: Full multi-turn context sent to CrewAI on every message
- **Markdown Rendering**: Responses rendered with proper Slack formatting

---

## Prerequisites

- Python 3.10+
- A Slack workspace where you can install apps (free Developer Sandbox available at [api.slack.com](https://api.slack.com))
- A deployed CrewAI API endpoint with its base URL and bearer token

---

## Step 1 — Create a Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App** → **From scratch**
3. Enter a name (e.g. `CrewAI Assistant`) and select your workspace
4. Click **Create App**

---

## Step 2 — Enable Agents & AI Apps

1. In the left sidebar click **Agents & AI Apps**
2. Toggle **Enable Agents & AI Apps** to On

This automatically adds the `assistant:write` scope required for the AI thread panel, suggested prompts, and status indicators.

---

## Step 3 — Add Bot Token Scopes

1. In the left sidebar click **OAuth & Permissions**
2. Scroll to **Scopes** → **Bot Token Scopes**
3. Click **Add an OAuth Scope** and add each of the following:

| Scope | Purpose |
|---|---|
| `app_mentions:read` | Receive events when the bot is @mentioned |
| `assistant:write` | Set status, title, and suggested prompts in AI threads (added automatically in Step 2) |
| `chat:write` | Post messages |
| `channels:history` | Read messages in public channels |
| `groups:history` | Read messages in private channels |
| `groups:read` | Access private channel info |
| `im:history` | Read direct messages |
| `reactions:write` | Add/remove emoji reactions |

---

## Step 4 — Enable Socket Mode

1. In the left sidebar click **Socket Mode**
2. Toggle **Enable Socket Mode** to On
3. Under **App-Level Tokens** click **Generate Token and Scopes**
4. Name the token (e.g. `socket-token`), add the `connections:write` scope, click **Generate**
5. Copy the token — it starts with `xapp-` — you'll need it later

---

## Step 5 — Subscribe to Events

1. In the left sidebar click **Event Subscriptions**
2. Toggle **Enable Events** to On
3. Under **Subscribe to bot events** click **Add Bot User Event** and add:

| Event | Purpose |
|---|---|
| `app_mention` | Bot is @mentioned in a channel |
| `assistant_thread_started` | User opens the AI assistant panel |
| `assistant_thread_context_changed` | User switches channels while panel is open |
| `message.channels` | Messages in public channels (for thread follow-ups) |
| `message.groups` | Messages in private channels (for thread follow-ups) |
| `message.im` | Direct messages |

4. Click **Save Changes**

---

## Step 6 — Install the App to Your Workspace

1. In the left sidebar click **Install App**
2. Click **Install to Workspace** and authorize
3. Copy the **Bot User OAuth Token** — it starts with `xoxb-`

---

## Step 7 — Configure Environment Variables

1. Copy the sample env file:
   ```bash
   cp .env.sample .env
   ```

2. Open `.env` and fill in your values:
   ```
   SLACK_BOT_TOKEN=xoxb-...      # From Step 6
   SLACK_APP_TOKEN=xapp-...      # From Step 4
   CREWAI_BASE_URL=https://...   # Your CrewAI API base URL
   CREWAI_BEARER_TOKEN=...       # Your CrewAI bearer token
   LOG_LEVEL=INFO                # DEBUG for verbose output, INFO for normal
   ```

---

## Step 8 — Install Dependencies and Run

```bash
pip install -r requirements.txt
python app.py
```

You should see:
```
⚡️ Slack bot is running!
```

---

## Usage

### AI Agent Thread (recommended)

Click the bot's name → **Message** to open the AI assistant panel. The bot will greet you with suggested prompts. All follow-up messages in the same thread are handled automatically — no @mention needed.

### Channel Thread

Mention the bot once in any message:
```
@CrewAI Assistant what are the Chase Freedom benefits?
```
The bot activates on that thread. All follow-up replies in the thread are handled automatically — no @mention needed after the first one.

### Private Channel

Same as a public channel. Make sure to first invite the bot:
```
/invite @CrewAI Assistant
```

---

## Troubleshooting

**Bot doesn't respond in channels**
- Run `/invite @yourbot` in the channel
- Check that `message.channels` (public) or `message.groups` (private) events are subscribed
- Verify Socket Mode is enabled and the bot is running

**Bot doesn't respond in private channels**
- Confirm `groups:history` and `groups:read` scopes are added and the app has been reinstalled after adding them
- Confirm `message.groups` is in your event subscriptions

**Status indicator not showing in channel threads**
- The `assistant:write` scope must be present — confirm it was added in Step 2 and reinstall the app

**`missing_scope` errors in logs**
- Add the missing scope under **OAuth & Permissions** → **Bot Token Scopes**, then reinstall the app via **Install App** → **Install to Workspace**

**Responses appear as raw markdown**
- This is a Slack client rendering issue — the bot sends Block Kit blocks which should render automatically in modern Slack clients
