#!/bin/bash

# Quick start script for Flask webhook demo

echo "🚀 Starting CrewAI Flask Webhook Demo"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please copy .env.sample to .env and configure your credentials:"
    echo "   cp .env.sample .env"
    echo ""
    exit 1
fi

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ Error: ngrok is not installed!"
    echo "📦 Install ngrok:"
    echo "   brew install ngrok/ngrok/ngrok"
    echo "   or visit https://ngrok.com/download"
    echo ""
    exit 1
fi

# Check if requirements are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Get port from .env or use default
PORT=$(grep PORT .env | cut -d '=' -f2 | tr -d ' ' || echo "5000")

echo "✅ Starting ngrok on port $PORT..."
echo "📡 ngrok dashboard: http://localhost:4040"
echo ""
echo "⚠️  Keep this terminal open and copy the ngrok URL"
echo "🌐 Access your app through the ngrok HTTPS URL"
echo ""
echo "Starting ngrok in 3 seconds..."
sleep 3

ngrok http $PORT
