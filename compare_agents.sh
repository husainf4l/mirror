#!/bin/bash

# Agent Comparison Demo Script
# Run both agents side-by-side for testing

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Wedding Mirror - Dual Agent Demo                  ║"
echo "║         Compare Agent 1 vs Agent 2 Side-by-Side          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if backend is running
echo -e "${YELLOW}🔍 Checking backend...${NC}"
if ! curl -s http://localhost:8000/api > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend not running!${NC}"
    echo "Please start backend first:"
    echo "  uvicorn backend.app.main:app --reload"
    exit 1
fi
echo -e "${GREEN}✅ Backend is running${NC}"
echo ""

# Check environment variables
echo -e "${YELLOW}🔍 Checking environment variables...${NC}"

# Check Agent 1 requirements
if [ -n "$GOOGLE_API_KEY" ]; then
    echo -e "${GREEN}✅ Agent 1 (Gemini): Ready${NC}"
    AGENT1_READY=true
else
    echo -e "${RED}❌ Agent 1 (Gemini): Missing GOOGLE_API_KEY${NC}"
    AGENT1_READY=false
fi

# Check Agent 2 requirements
if [ -n "$OPENAI_API_KEY" ] && [ -n "$ELEVENLABS_API_KEY" ]; then
    echo -e "${GREEN}✅ Agent 2 (Pipeline): Ready${NC}"
    AGENT2_READY=true
else
    echo -e "${RED}❌ Agent 2 (Pipeline): Missing OPENAI_API_KEY or ELEVENLABS_API_KEY${NC}"
    AGENT2_READY=false
fi

echo ""

if ! $AGENT1_READY && ! $AGENT2_READY; then
    echo -e "${RED}❌ No agents ready! Please set up API keys in .env${NC}"
    exit 1
fi

# Display comparison
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    AGENT COMPARISON                        ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  Feature          │  Agent 1 (Gemini)  │  Agent 2 (STT→TTS)║"
echo "║  ────────────────────────────────────────────────────────  ║"
echo "║  Latency          │  ⚡ <200ms         │  ⏱️  500-1000ms   ║"
echo "║  Cost             │  💰 \$0.08          │  💵 \$0.21         ║"
echo "║  Vision           │  ✅ Yes            │  ❌ No            ║"
echo "║  Voice Options    │  1 voice           │  50+ voices      ║"
echo "║  Customization    │  Limited           │  Full control    ║"
echo "║  Setup            │  Simple            │  Moderate        ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Ask which agents to start
echo -e "${YELLOW}Which agents would you like to start?${NC}"
echo "1) Agent 1 only (Gemini Realtime)"
echo "2) Agent 2 only (Standard Pipeline)"
echo "3) Both agents (for comparison)"
echo "4) Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        if ! $AGENT1_READY; then
            echo -e "${RED}❌ Agent 1 not configured!${NC}"
            exit 1
        fi
        echo ""
        echo -e "${BLUE}🎭 Starting Agent 1 (Gemini Realtime)...${NC}"
        cd agent
        python agent.py dev
        ;;
    2)
        if ! $AGENT2_READY; then
            echo -e "${RED}❌ Agent 2 not configured!${NC}"
            exit 1
        fi
        echo ""
        echo -e "${BLUE}🤖 Starting Agent 2 (Standard Pipeline)...${NC}"
        cd agent2
        ./start.sh
        ;;
    3)
        if ! $AGENT1_READY || ! $AGENT2_READY; then
            echo -e "${RED}❌ Both agents must be configured!${NC}"
            exit 1
        fi
        echo ""
        echo -e "${GREEN}🚀 Starting both agents...${NC}"
        echo ""
        echo -e "${BLUE}Agent 1${NC} will run in background"
        echo -e "${BLUE}Agent 2${NC} will run in foreground"
        echo ""
        echo "Connect to different LiveKit rooms to test each agent separately!"
        echo ""
        
        # Start Agent 1 in background
        cd agent
        python agent.py dev &
        AGENT1_PID=$!
        cd ..
        
        sleep 2
        
        # Start Agent 2 in foreground
        cd agent2
        ./start.sh
        
        # Cleanup on exit
        echo ""
        echo "Stopping Agent 1..."
        kill $AGENT1_PID
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice!${NC}"
        exit 1
        ;;
esac
