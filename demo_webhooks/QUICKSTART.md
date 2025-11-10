# Quick Start Guide

## Prerequisites

1. **Install ngrok** (if not already installed):
   ```bash
   brew install ngrok/ngrok/ngrok
   ```

2. **Configure ngrok** with your authtoken (get it from [ngrok.com](https://ngrok.com)):
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

You need **two terminal windows**:

### Terminal 1: Start ngrok

```bash
cd demo_webhooks
./start.sh
```

This will:
- Start ngrok on port 5000
- Display the public URL (e.g., `https://abc123.ngrok-free.app`)
- Keep running (don't close this terminal!)

### Terminal 2: Start Flask

```bash
cd demo_webhooks
./run_flask.sh
```

This will:
- Start the Flask application on `http://localhost:5000`
- Keep running (don't close this terminal!)

## Access the App

Open your browser and go to the **ngrok URL** from Terminal 1:
```
https://abc123.ngrok-free.app
```

**Important:** Use the ngrok URL (not localhost) so webhooks can reach your server!

## Quick Test

1. Open the ngrok URL in your browser
2. Type a message: "What are travel benefits?"
3. Wait for the CrewAI response
4. Continue the conversation!

## Monitoring

- **ngrok dashboard**: [http://localhost:4040](http://localhost:4040)
  - See all incoming webhook requests
  - Debug webhook payloads
  - View response times

## Troubleshooting

### "ngrok not found"
```bash
brew install ngrok/ngrok/ngrok
```

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Webhooks not working
1. Check ngrok is running (Terminal 1)
2. Verify you're using the ngrok URL (not localhost)
3. Check ngrok dashboard at http://localhost:4040

### No response from CrewAI
1. Verify `.env` credentials are correct
2. Check Flask terminal for errors
3. Check ngrok dashboard for webhook callbacks

## Stop the App

1. Press `Ctrl+C` in Terminal 2 (Flask)
2. Press `Ctrl+C` in Terminal 1 (ngrok)

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the code in `app.py` and `templates/index.html`
- Check out the [CrewAI documentation](https://docs.crewai.com)
