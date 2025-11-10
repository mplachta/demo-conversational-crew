# CrewAI Chat - Flask Webhook Demo

A Flask-based chat application that demonstrates CrewAI conversational agents using webhooks instead of polling. This implementation uses ngrok to expose a local webhook endpoint for receiving CrewAI callbacks.

## Features

- **Webhook-based architecture**: Receives real-time callbacks from CrewAI instead of polling
- **Modern chat UI**: Clean, responsive interface similar to the Streamlit demo
- **Session management**: Maintains conversation context across messages
- **ngrok integration**: Easy local development with public webhook URLs

## Architecture

```
User → Flask Frontend → CrewAI API (with webhook URL)
                            ↓
Flask Webhook Endpoint ← CrewAI Callback
        ↓
Frontend (SSE) ← Real-time Push
```

## Prerequisites

- Python 3.10+
- ngrok account (free tier works fine)
- CrewAI API credentials

## Installation

### 1. Install Dependencies

```bash
cd demo_webhooks
pip install -r requirements.txt
```

### 2. Install ngrok

**macOS (using Homebrew):**
```bash
brew install ngrok/ngrok/ngrok
```

**Or download directly:**
Visit [ngrok.com/download](https://ngrok.com/download) and follow the installation instructions.

### 3. Configure ngrok

Sign up at [ngrok.com](https://ngrok.com) and get your authtoken, then:

```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

### 4. Set Up Environment Variables

Copy the sample environment file:
```bash
cp .env.sample .env
```

Edit `.env` with your credentials:
```env
CREWAI_BASE_URL=https://api.crewai.com/v1
CREWAI_BEARER_TOKEN=your_bearer_token_here
FLASK_SECRET_KEY=your_random_secret_key_here
FLASK_DEBUG=False
PORT=5000
```

**Note:** You can generate a secure secret key with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Running the Application

### Step 1: Start ngrok

In a terminal window, start ngrok to expose your local Flask app:

```bash
ngrok http 5000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:5000
```

**Important:** Keep this terminal window open while using the app.

### Step 2: Start Flask App

In a new terminal window:

```bash
cd demo_webhooks
python app.py
```

The Flask app will start on `http://localhost:5000`

### Step 3: Access the Application

Open your browser and navigate to the ngrok URL shown in Step 1:
```
https://abc123.ngrok-free.app
```

**Note:** You can also access it locally at `http://localhost:5000`, but webhooks will only work through the ngrok URL since CrewAI needs to reach your local server.

## How It Works

### 1. Message Flow

1. User sends a message through the web interface
2. Frontend sends POST request to `/api/send_message`
3. Frontend opens SSE connection to `/api/stream/{kickoff_id}`
4. Backend forwards the message to CrewAI API with webhook URL
5. CrewAI processes the request asynchronously
6. CrewAI sends callback to `/api/webhook` when complete
7. Backend pushes result to frontend via SSE
8. Response is displayed in the chat instantly

### 2. Webhook Endpoint

The webhook endpoint (`/api/webhook`) receives callbacks from CrewAI:

```python
@app.route("/api/webhook", methods=["POST"])
def webhook():
    data = request.json
    kickoff_id = data.get("kickoff_id")
    state = data.get("state")
    result = data.get("result")
    # Store result for frontend polling
```

### 3. Session Management

Conversation IDs are stored in Flask sessions to maintain context:

```python
session["crewai_conversation_id"] = response_data["conversation_id"]
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve the chat interface |
| `/api/send_message` | POST | Send a message to CrewAI |
| `/api/webhook` | POST | Receive CrewAI callbacks |
| `/api/stream/<kickoff_id>` | GET | SSE stream for real-time results |
| `/api/update_session` | POST | Update session with conversation ID |

## Troubleshooting

### Webhooks Not Working

1. **Check ngrok is running**: Ensure ngrok terminal is still active
2. **Verify webhook URL**: The app automatically uses `request.host_url` which should be the ngrok URL
3. **Check ngrok dashboard**: Visit [http://localhost:4040](http://localhost:4040) to see incoming requests
4. **Firewall issues**: Ensure ngrok can receive incoming connections

### Connection Errors

1. **CrewAI API credentials**: Verify your `CREWAI_BASE_URL` and `CREWAI_BEARER_TOKEN` in `.env`
2. **Network issues**: Check your internet connection
3. **API endpoint**: Ensure the CrewAI API endpoint is correct

### Session Issues

1. **Secret key**: Make sure `FLASK_SECRET_KEY` is set in `.env`
2. **Browser cookies**: Clear browser cookies and try again

## Development Tips

### View ngrok Traffic

ngrok provides a web interface to inspect all HTTP traffic:
```
http://localhost:4040
```

This is invaluable for debugging webhook callbacks.

### Enable Debug Mode

For development, enable Flask debug mode in `.env`:
```env
FLASK_DEBUG=True
```

**Warning:** Never use debug mode in production!

### Custom Port

To use a different port, update `.env`:
```env
PORT=8000
```

Then restart ngrok:
```bash
ngrok http 8000
```

## Production Deployment

For production deployment:

1. **Use a proper web server**: Deploy with Gunicorn or uWSGI
2. **Use a real domain**: Replace ngrok with a proper domain and SSL
3. **Use Redis**: Replace in-memory `webhook_responses` dict with Redis
4. **Add authentication**: Implement proper user authentication
5. **Add rate limiting**: Protect your endpoints from abuse
6. **Environment variables**: Use proper secret management

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Comparison with Streamlit Demo

| Feature | Streamlit Demo | Flask Webhook Demo |
|---------|---------------|-------------------|
| Architecture | Polling | Webhooks + SSE |
| Response Time | Slower (polling interval) | Instant (real-time push) |
| Server Load | Higher (continuous polling) | Lower (event-driven) |
| Complexity | Simple | Moderate |
| Scalability | Limited | Better |

## Example Questions

Try asking the crew:
- "What are travel benefits?"
- "What are the coverage limits?"
- "What are the benefits of Chase Freedom?"

## License

This demo is part of the CrewAI conversational routing project.

## Support

For issues or questions:
- CrewAI Documentation: [docs.crewai.com](https://docs.crewai.com)
- ngrok Documentation: [ngrok.com/docs](https://ngrok.com/docs)
