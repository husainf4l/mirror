#!/bin/bash

# Wedding Mirror Agent 2 - Quick Start Script
# This script sets up and runs the standard pipeline agent

set -e

echo "🎭 Wedding Mirror - Agent 2 (Standard Pipeline) Startup"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please create a virtual environment first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
source ../venv/bin/activate

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create a .env file in the project root with:"
    echo "  OPENAI_API_KEY=your-key"
    echo "  ELEVENLABS_API_KEY=your-key"
    echo "  LIVEKIT_URL=wss://your-server"
    echo "  LIVEKIT_API_KEY=your-key"
    echo "  LIVEKIT_API_SECRET=your-secret"
    echo ""
    echo "You can copy from agent2/.env.example"
    exit 1
fi

# Check for required environment variables
echo -e "${YELLOW}🔍 Checking environment variables...${NC}"

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY not set${NC}"
    exit 1
fi

if [ -z "$ELEVENLABS_API_KEY" ]; then
    echo -e "${RED}❌ ELEVENLABS_API_KEY not set${NC}"
    exit 1
fi

if [ -z "$LIVEKIT_URL" ]; then
    echo -e "${RED}❌ LIVEKIT_URL not set${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All required environment variables are set${NC}"
echo ""

# Display configuration
echo -e "${YELLOW}⚙️  Configuration:${NC}"
echo "  STT: OpenAI Whisper"
echo "  LLM: OpenAI GPT-4o"
echo "  TTS: ElevenLabs"
echo "  Voice: ${ELEVENLABS_VOICE_ID:-Rachel (default)}"
echo ""

# Check if backend is running
echo -e "${YELLOW}🔌 Checking backend connection...${NC}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
if curl -s "$BACKEND_URL/api" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running at $BACKEND_URL${NC}"
else
    echo -e "${YELLOW}⚠️  Backend not responding at $BACKEND_URL${NC}"
    echo "   Make sure to start the backend first:"
    echo "   Run the 'Start FastAPI Server' task"
fi
echo ""

# Start the agent
echo -e "${GREEN}🚀 Starting Agent 2 (Standard Pipeline)...${NC}"
echo ""
echo -e "${YELLOW}📝 Instructions:${NC}"
echo "  1. Join the LiveKit room from your frontend"
echo "  2. Say 'mirror mirror' to activate"
echo "  3. Follow the conversation flow"
echo "  4. Press Ctrl+C to stop"
echo ""
echo "=================================================="
echo ""

# Set Python path and run agent
export PYTHONPATH="${PYTHONPATH}:$(dirname $PWD)"
python agent.py dev
