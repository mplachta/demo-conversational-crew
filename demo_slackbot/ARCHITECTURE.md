# Slack Bot Architecture

## Overview

This Slack bot integrates with CrewAI's conversational routing system to provide intelligent, context-aware responses in Slack channels and threads.

## Components

### 1. Slack Bolt Framework (`app.py`)

The bot uses Slack's Bolt framework for Python, which provides:
- Event handling for Slack events
- Socket Mode for real-time communication
- Built-in middleware and error handling

### 2. Event Handlers

#### `handle_mention(event, say, client)`
- **Trigger**: When the bot is mentioned with `@botname`
- **Process**:
  1. Extract user message (removing bot mention)
  2. Determine thread context (thread_ts)
  3. Generate or retrieve session ID
  4. Call ChatFlow with message and session
  5. Send response back to thread

#### `handle_message_events(body, logger)`
- **Trigger**: General message events
- **Purpose**: Required for Slack Events API, currently logs only

### 3. Session Management

```python
conversation_sessions = {}  # In-memory session store

def get_session_id(channel_id: str, thread_ts: str = None) -> str:
    """Generate unique session ID per thread"""
    if thread_ts:
        return f"{channel_id}_{thread_ts}"
    return channel_id
```

**Session Strategy**:
- Each thread gets a unique session ID: `{channel_id}_{thread_ts}`
- Session IDs map to CrewAI Flow state IDs
- Enables conversation continuity within threads
- Different threads maintain separate contexts

### 4. CrewAI Integration

```python
from src.conversational_routing.main import ChatFlow

chat_flow = ChatFlow()
inputs = {"current_message": message}

if session_id in conversation_sessions:
    inputs["id"] = conversation_sessions[session_id]

response = chat_flow.kickoff(inputs=inputs)
conversation_sessions[session_id] = chat_flow.state.id
```

**Flow**:
1. Create ChatFlow instance
2. Pass current message
3. Include session ID if continuing conversation
4. ChatFlow uses `@persist()` to maintain state
5. Store returned state ID for future messages

## Data Flow

```
┌─────────────────┐
│  Slack User     │
│  mentions bot   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Slack Event    │
│  (app_mention)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Socket Mode    │
│  Handler        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  handle_mention()               │
│  - Extract message              │
│  - Get/create session ID        │
│  - Retrieve conversation state  │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  ChatFlow.kickoff()             │
│  - Classify message             │
│  - Route to appropriate agent   │
│  - Generate response            │
│  - Update conversation history  │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Store session state            │
│  conversation_sessions[id] = .. │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│  say()          │
│  Send to Slack  │
│  in thread      │
└─────────────────┘
```

## Thread Handling

### Thread Detection
```python
thread_ts = event.get("thread_ts") or event.get("ts")
```
- If message is in a thread: use `thread_ts`
- If new message: use message `ts` as thread starter

### Thread Response
```python
say(
    text=response_data["response"],
    thread_ts=thread_ts
)
```
- Always respond in the same thread
- Maintains conversation context visually
- Keeps channels organized

## Session Persistence

### Current Implementation (In-Memory)
- **Pros**: Simple, fast
- **Cons**: Lost on restart, not scalable

### Production Considerations
For production, consider:
1. **Redis**: Fast, distributed session store
2. **Database**: PostgreSQL/MongoDB for persistence
3. **CrewAI's built-in persistence**: Already handles Flow state

```python
# Example Redis integration
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

def get_session_id_from_redis(session_key):
    return r.get(session_key)

def store_session_id_in_redis(session_key, flow_id):
    r.set(session_key, flow_id, ex=86400)  # 24hr expiry
```

## Error Handling

```python
try:
    # Process message
except Exception as e:
    logger.error(f"Error handling mention: {str(e)}", exc_info=True)
    say(
        text="Sorry, I encountered an error...",
        thread_ts=thread_ts
    )
```

- Catch all exceptions to prevent bot crashes
- Log errors with full traceback
- Send user-friendly error message
- Maintain thread context even in errors

## Security Considerations

1. **Token Management**
   - Store tokens in `.env` file
   - Never commit tokens to version control
   - Use environment variables

2. **Input Validation**
   - Slack handles most validation
   - Bot strips mention tags
   - Empty message handling

3. **Rate Limiting**
   - Consider implementing for production
   - Prevent abuse and API quota exhaustion

## Scalability

### Current Limitations
- Single process
- In-memory session storage
- No load balancing

### Scaling Strategies
1. **Horizontal Scaling**
   - Multiple bot instances
   - Shared session store (Redis)
   - Load balancer

2. **Async Processing**
   - Queue long-running tasks
   - Background workers for CrewAI flows
   - Immediate acknowledgment to Slack

3. **Caching**
   - Cache common responses
   - Reduce CrewAI API calls
   - Faster response times

## Monitoring & Logging

Current logging:
```python
logging.basicConfig(level=logging.INFO)
logger.info(f"Processing message from user {user}")
logger.error(f"Error handling mention: {str(e)}", exc_info=True)
```

Production additions:
- Structured logging (JSON)
- Log aggregation (ELK, Datadog)
- Performance metrics
- Error tracking (Sentry)
- Usage analytics

## Future Enhancements

1. **Rich Message Formatting**
   - Slack Block Kit for interactive messages
   - Buttons, dropdowns, modals
   - Better visual presentation

2. **Direct Messages**
   - Support DMs in addition to mentions
   - Private conversations

3. **Slash Commands**
   - `/chase-benefits` command
   - Quick actions

4. **Interactive Components**
   - Buttons for common questions
   - Feedback collection
   - Action confirmations

5. **Multi-workspace Support**
   - Support multiple Slack workspaces
   - Workspace-specific configurations
