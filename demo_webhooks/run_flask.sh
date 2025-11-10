#!/bin/bash

# Script to run Flask app

echo "🚀 Starting Flask application..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please copy .env.sample to .env and configure your credentials:"
    echo "   cp .env.sample .env"
    echo ""
    exit 1
fi

# Check if requirements are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Get port
PORT=${PORT:-5000}

echo "✅ Flask app starting on http://localhost:$PORT"
echo "📝 Make sure ngrok is running in another terminal:"
echo "   ./start.sh"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Flask app
python app.py
