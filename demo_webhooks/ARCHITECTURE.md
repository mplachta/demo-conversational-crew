# Architecture Overview

## System Architecture

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐      ┌──────────┐
│    Flask    │◄────►│  ngrok   │
│   Backend   │      │  Proxy   │
└──────┬──────┘      └──────────┘
       │                    ▲
       │ HTTPS              │ HTTPS
       ▼                    │
┌─────────────┐            │
│  CrewAI API │────────────┘
│   (Remote)  │  Webhook Callback
└─────────────┘
```

## Request Flow

### 1. User Sends Message

```
User → Frontend → Flask Backend
                      │
                      ├─ Store in session
                      └─ POST to CrewAI API
                         {
                           "inputs": {...},
                           "webhook": "https://abc123.ngrok-free.app/api/webhook"
                         }
```

### 2. CrewAI Processing

```
CrewAI API receives request
    │
    ├─ Returns kickoff_id immediately
    │
    └─ Processes asynchronously
           │
           └─ When complete, sends webhook callback
```

### 3. Webhook Callback

```
CrewAI → ngrok → Flask /api/webhook
                    │
                    └─ Store result in memory
                       (keyed by kickoff_id)
```

### 4. Real-time Push via SSE

```
Frontend opens SSE connection to /api/stream/{kickoff_id}
    │
    └─ Waits for webhook result
           │
           └─ Receives response instantly when ready
```

## Key Components

### Flask Backend (`app.py`)

**Endpoints:**
- `GET /` - Serve HTML frontend
- `POST /api/send_message` - Send message to CrewAI
- `POST /api/webhook` - Receive CrewAI callbacks
- `GET /api/stream/<id>` - SSE stream for real-time results
- `POST /api/update_session` - Update session with conversation ID

**State Management:**
- Session: Stores `crewai_conversation_id` for context
- Memory dict: Stores webhook responses temporarily

### Frontend (`templates/index.html`)

**Features:**
- Chat interface with message history
- Real-time message sending
- Server-Sent Events (SSE) for instant updates
- Loading states and error handling
- Responsive design

### ngrok

**Purpose:**
- Exposes local Flask server to the internet
- Provides HTTPS endpoint for webhooks
- Enables local development with external APIs

**Benefits:**
- No deployment needed for testing
- Inspect all webhook traffic
- Free tier available

## Data Flow

### Message Structure

**User Message:**
```json
{
  "message": "What are travel benefits?"
}
```

**CrewAI Request:**
```json
{
  "inputs": {
    "current_message": "What are travel benefits?",
    "id": "conversation_123"  // if continuing conversation
  },
  "webhook": "https://abc123.ngrok-free.app/api/webhook"
}
```

**CrewAI Response (to webhook):**
```json
{
  "kickoff_id": "kickoff_456",
  "state": "SUCCESS",
  "result": "{\"response\": \"Travel benefits include...\", \"id\": \"conversation_123\"}"
}
```

**Frontend Response:**
```json
{
  "status": "complete",
  "response": "Travel benefits include..."
}
```

## Comparison: Polling vs Webhooks + SSE

### Streamlit Demo (Polling)

```
User → Streamlit → CrewAI API
                       │
                       └─ Returns kickoff_id
                       
Streamlit polls /status/{kickoff_id} every 1 second
    │
    └─ Until state == "SUCCESS"
```

**Pros:**
- Simpler implementation
- No external URL needed
- Works anywhere

**Cons:**
- Higher server load (continuous polling)
- Slower response time (polling interval)
- Wastes resources checking incomplete tasks

### Flask Demo (Webhooks + SSE)

```
User → Flask → CrewAI API (with webhook URL)
                   │
                   └─ Returns kickoff_id
                   
Frontend opens SSE connection to /api/stream/{kickoff_id}
    │
    └─ Waits for webhook
    
CrewAI → Webhook → Flask pushes to SSE client
                       │
                       └─ Frontend receives instantly
```

**Pros:**
- Lowest server load (event-driven, no polling)
- Instant response time (real-time push)
- Most scalable architecture
- Production-ready pattern
- True real-time communication

**Cons:**
- Requires public URL (ngrok for local dev)
- More complex setup
- Need to manage SSE connections

## Session Management

### Conversation Context

Flask sessions maintain conversation state:

```python
# First message
session['crewai_conversation_id'] = None

# After first response
session['crewai_conversation_id'] = 'conversation_123'

# Subsequent messages include conversation ID
inputs = {
    "current_message": "...",
    "id": session['crewai_conversation_id']  # Maintains context
}
```

### Benefits:
- Multi-turn conversations
- Context preservation
- User-specific state
- Automatic cleanup on session end

## Error Handling

### Network Errors
```python
try:
    response = requests.post(...)
except Exception as e:
    return jsonify({"error": str(e)}), 500
```

### Timeout Handling
```javascript
const maxAttempts = 60; // 60 seconds
while (attempts < maxAttempts) {
    // Poll for result
    if (complete) return result;
    await sleep(1000);
}
throw new Error('Timeout');
```

### Webhook Failures
- CrewAI retries failed webhooks
- Frontend falls back to polling if webhook doesn't arrive
- Error messages displayed in chat

## Security Considerations

### Current Implementation (Development)
- Session-based auth
- In-memory state storage
- Debug mode enabled
- ngrok free tier (public URLs)

### Production Recommendations
1. **Authentication**: Implement proper user auth
2. **HTTPS**: Use real SSL certificates
3. **Rate Limiting**: Protect endpoints from abuse
4. **State Storage**: Use Redis instead of memory dict
5. **Webhook Verification**: Verify webhook signatures
6. **Environment Variables**: Use secret management service
7. **CORS**: Configure proper CORS policies
8. **Input Validation**: Sanitize all user inputs

## Scaling Considerations

### Current Limitations
- In-memory storage (single server only)
- No load balancing
- Session affinity required

### Production Scaling
1. **Redis**: For distributed webhook storage
2. **Load Balancer**: Distribute traffic across servers
3. **Message Queue**: Use RabbitMQ/Redis for async processing
4. **Database**: Store conversation history
5. **CDN**: Serve static assets
6. **Monitoring**: Add logging and metrics

## Development Workflow

### Local Development
1. Start ngrok: `./start.sh`
2. Start Flask: `./run_flask.sh`
3. Access via ngrok URL
4. Monitor ngrok dashboard: http://localhost:4040

### Testing Webhooks
1. Send test message
2. Check ngrok dashboard for webhook POST
3. Verify payload in Flask logs
4. Confirm response in frontend

### Debugging
- **Flask logs**: Check terminal output
- **ngrok dashboard**: Inspect HTTP traffic
- **Browser console**: Check JavaScript errors
- **Network tab**: Monitor API calls

## Future Enhancements

### Potential Improvements
1. **WebSockets**: Real-time bidirectional communication
2. **Message Queue**: Better async handling
3. **Caching**: Cache common responses
4. **Analytics**: Track usage patterns
5. **Multi-user**: Support multiple concurrent users
6. **Persistence**: Save conversation history
7. **Export**: Download chat transcripts
8. **Themes**: Dark/light mode toggle
9. **Voice**: Speech-to-text input
10. **Mobile**: Responsive mobile app

## Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **ngrok Documentation**: https://ngrok.com/docs
- **CrewAI Documentation**: https://docs.crewai.com
- **Webhook Best Practices**: https://webhooks.fyi/
