# Agent 2 - Quick Setup Guide

Get Agent 2 (Standard Pipeline) up and running in 5 minutes!

## Prerequisites

✅ Python 3.12+ installed  
✅ Virtual environment activated  
✅ Backend server running  
✅ LiveKit server accessible  

## Step 1: Install Dependencies

```bash
# From project root
pip install -r requirements.txt
```

This will install:
- `livekit-plugins-elevenlabs` - For TTS
- `livekit-plugins-openai` - For STT and LLM
- `livekit-plugins-silero` - For VAD
- All other required packages

## Step 2: Get API Keys

### OpenAI API Key (Required)
1. Visit: https://platform.openai.com/api-keys
2. Create new secret key
3. Copy the key (starts with `sk-`)

### ElevenLabs API Key (Required)
1. Visit: https://elevenlabs.io/app/settings/api-keys
2. Sign up for free (10,000 characters/month)
3. Create new API key
4. Copy the key

### LiveKit Credentials (Required)
- Use existing credentials from main agent
- Or create new project at https://cloud.livekit.io

## Step 3: Configure Environment

Create or update `.env` file in project root:

```env
# OpenAI (for Whisper + GPT-4)
OPENAI_API_KEY=sk-your-openai-key-here

# ElevenLabs (for TTS)
ELEVENLABS_API_KEY=your-elevenlabs-key-here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Optional: Rachel voice

# LiveKit (same as Agent 1)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret

# Backend
BACKEND_URL=http://localhost:8000
```

**Pro Tip:** Copy from `agent2/.env.example` as a template!

## Step 4: Choose Your Voice

ElevenLabs offers many voices. Popular options:

| Voice ID | Name | Description |
|----------|------|-------------|
| `21m00Tcm4TlvDq8ikWAM` | Rachel | Warm, friendly female (default) |
| `EXAVITQu4vr4xnSDxMaL` | Bella | Soft, gentle female |
| `ThT5KcBeYPX3keUQqHPh` | Dorothy | Pleasant, mature female |
| `ErXwobaYiN019PkySvjV` | Antoni | Well-rounded male |
| `TxGEqnHWrfWFTfGW9XjX` | Josh | Deep, authoritative male |

Set `ELEVENLABS_VOICE_ID` in `.env` to change voice.

**Try voices at:** https://elevenlabs.io/voice-library

## Step 5: Start the Agent

### Option A: Using the Script (Recommended)
```bash
cd agent2
./start.sh
```

The script will:
- ✅ Check environment variables
- ✅ Verify backend connection
- ✅ Display configuration
- ✅ Start the agent

### Option B: Using VS Code Task
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Run Task"
3. Select **"Start Agent 2 - Standard Pipeline"**

### Option C: Manual Start
```bash
cd agent2
source ../venv/bin/activate
export PYTHONPATH="$(dirname $PWD):$PYTHONPATH"
python agent.py dev
```

## Step 6: Test the Agent

1. **Open your frontend** (React app)
2. **Join the LiveKit room** 
3. **Say "mirror mirror"** to activate
4. **Have a conversation!**

### Expected Flow:
```
You: "mirror mirror"
Agent: "Ding ding! Oh, welcome dear guest! What is your name?"
You: "I'm Sarah"
Agent: *updates display with "Welcome Sarah!"*
You: "Thank you!"
Agent: *gives compliments*
...
You: "Goodbye"
Agent: *calls close_session(), resets mirror*
```

## Troubleshooting

### ❌ "OpenAI API key not set"
**Solution:** Check `.env` file has `OPENAI_API_KEY=sk-...`

### ❌ "ElevenLabs API key not set"
**Solution:** Check `.env` file has `ELEVENLABS_API_KEY=...`

### ❌ Agent doesn't respond
**Solutions:**
- Check microphone permissions
- Verify LiveKit connection
- Look for "mirror mirror" detection in logs
- Try saying it louder/clearer

### ❌ High latency / Slow responses
**Solutions:**
```python
# In agent.py, change to faster models:
llm=openai.LLM(model="gpt-4o-mini")  # Faster, cheaper
tts=elevenlabs.TTS(
    model="eleven_turbo_v2",  # Fastest model
    latency=1,  # Optimize for speed
)
```

### ❌ "Backend not reachable"
**Solution:** Start backend first:
```bash
# Run in another terminal
cd backend
uvicorn app.main:app --reload
```

### ❌ Poor voice quality
**Solutions:**
- Try different voice IDs (see Step 4)
- Check internet bandwidth
- Verify ElevenLabs quota not exceeded

### ❌ Import errors
**Solution:** Reinstall dependencies:
```bash
pip install -r requirements.txt --upgrade
```

## Verify Installation

Run this quick test:

```bash
cd agent2
python -c "
from livekit.plugins import openai, elevenlabs, silero
print('✅ All plugins imported successfully!')
"
```

If you see "✅ All plugins imported successfully!" - you're ready!

## Cost Monitoring

### ElevenLabs Free Tier:
- 10,000 characters/month
- ~3-5 conversations of 3 minutes each
- Upgrade to Creator ($5/month) for 30,000 characters

### OpenAI Costs:
- Whisper: $0.006 per minute
- GPT-4o: $5/$15 per 1M tokens
- Average conversation: ~$0.02-0.05

**Pro Tip:** Start with free tiers, monitor usage, upgrade as needed!

## Next Steps

✅ Agent 2 is running!

Now you can:
- 📊 Compare with Agent 1 (see `COMPARISON.md`)
- 🎨 Customize the personality in `agent.py`
- 🔊 Try different voices
- 📈 Monitor costs and performance
- 🚀 Deploy to production

## Need Help?

- 📖 Read `README.md` for detailed documentation
- 🔄 Check `COMPARISON.md` for Agent 1 vs Agent 2
- 🐛 Enable debug logging: `export LOG_LEVEL=DEBUG`
- 💬 Check LiveKit logs in console

## Quick Reference

**Start Agent:**
```bash
cd agent2 && ./start.sh
```

**Stop Agent:**
```
Ctrl+C
```

**Check Status:**
```bash
curl http://localhost:8000/api
```

**View Logs:**
```bash
# In agent2 directory
tail -f *.log  # If logging to file
```

Happy mirroring! 🪞✨
