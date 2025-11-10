#!/usr/bin/env python
"""
Flask-based chat application with webhook support for CrewAI conversational agents.
"""
import os
import json
import requests
from flask import Flask, render_template, request, jsonify, session, Response
from dotenv import load_dotenv
import secrets
import queue

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))

# CrewAI API configuration
BASE_URL = os.getenv("CREWAI_BASE_URL")
BEARER_TOKEN = os.getenv("CREWAI_BEARER_TOKEN")
WEBHOOK_BEARER_TOKEN = os.getenv("WEBHOOK_BEARER_TOKEN")
WEBHOOK_URL_BASE = os.getenv("WEBHOOK_URL_BASE")
HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

# Store for webhook responses (in production, use Redis or database)
webhook_responses = {}

# Store for SSE clients (execution_id -> queue)
sse_clients = {}


@app.route("/")
def index():
    """Render the chat interface."""
    return render_template("index.html")


@app.route("/api/send_message", methods=["POST"])
def send_message():
    """
    Send a message to the CrewAI API with webhook callback.
    """
    data = request.json
    message = data.get("message")
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    # Get or initialize conversation ID
    conversation_id = session.get("crewai_conversation_id")
    
    # Prepare inputs for CrewAI
    inputs = {"current_message": message}
    if conversation_id:
        inputs["id"] = conversation_id
    
    # Get the webhook URL (ngrok URL + /webhook endpoint)
    webhook_url = f"{WEBHOOK_URL_BASE}/api/webhook"
    
    # Make request to CrewAI with webhook
    try:
        response = requests.post(
            f"{BASE_URL}/kickoff",
            json={
                "inputs": inputs,
                "webhooks": {
                    "events": ["flow_finished"],
                    "url": webhook_url,
                    "realtime": True,
                    "authentication": {
                        "strategy": "bearer",
                        "token": WEBHOOK_BEARER_TOKEN
                    }
                }
            },
            headers=HEADERS
        )
        
        if response.ok:
            kickoff_id = response.json().get("kickoff_id")
            return jsonify({
                "status": "processing",
                "kickoff_id": kickoff_id
            })
        else:
            return jsonify({"error": response.text}), response.status_code
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/webhook", methods=["POST"])
def webhook():
    """
    Receive webhook callback from CrewAI when processing is complete.
    """
    data = request.json
    
    # Handle new webhook format with events array
    events = data.get("events", [])
    
    for event in events:
        event_type = event.get("type")
        execution_id = event.get("execution_id")
        event_data = event.get("data", {})
        
        # Process flow_finished events
        if event_type == "flow_finished":
            result = event_data.get("result")
            
            if result:
                # Parse the result JSON string
                result_data = json.loads(result)
                
                # Store the response using execution_id as the key
                webhook_responses[execution_id] = {
                    "response": result_data.get("response"),
                    "conversation_id": result_data.get("id")
                }
                
                # Push to SSE client if connected
                if execution_id in sse_clients:
                    try:
                        sse_clients[execution_id].put({
                            "response": result_data.get("response"),
                            "conversation_id": result_data.get("id")
                        })
                    except Exception:
                        # Client may have disconnected, ignore
                        pass
    
    return jsonify({"status": "received"}), 200


@app.route("/api/stream/<kickoff_id>")
def stream(kickoff_id):
    """
    Server-Sent Events endpoint for real-time webhook results.
    """
    def event_stream():
        # Create a queue for this client
        client_queue = queue.Queue()
        sse_clients[kickoff_id] = client_queue
        
        try:
            # Check if result already exists (webhook arrived before SSE connection)
            if kickoff_id in webhook_responses:
                response_data = webhook_responses.pop(kickoff_id)
                yield f"data: {json.dumps(response_data)}\n\n"
                return
            
            # Wait for webhook callback (timeout after 60 seconds)
            try:
                response_data = client_queue.get(timeout=60)
                yield f"data: {json.dumps(response_data)}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'error': 'Timeout waiting for response'})}\n\n"
        finally:
            # Clean up
            if kickoff_id in sse_clients:
                del sse_clients[kickoff_id]
    
    response = Response(event_stream(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@app.route("/api/update_session", methods=["POST"])
def update_session():
    """Update session with conversation ID."""
    data = request.json
    conversation_id = data.get("conversation_id")
    
    if conversation_id:
        session["crewai_conversation_id"] = conversation_id
        return jsonify({"status": "updated"})
    
    return jsonify({"error": "conversation_id required"}), 400


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
