# Wedding Mirror Agent 2 - Standard Pipeline

This is the second implementation of the Wedding Mirror Agent using the standard LiveKit pipeline architecture with traditional STT → LLM → TTS flow.

## Architecture

```
User Speech → Whisper (STT) → GPT-4 (LLM) → ElevenLabs (TTS) → Audio Output
```

### Components

1. **Speech-to-Text (STT):** OpenAI Whisper
   - Model: `whisper-1`
   - Language: English (configurable)
   - High accuracy transcription

2. **Large Language Model (LLM):** OpenAI GPT-4
   - Model: `gpt-4o`
   - Temperature: 0.7
   - Function calling support

3. **Text-to-Speech (TTS):** ElevenLabs
   - Model: `eleven_turbo_v2_5`
   - Voice: Rachel (default, configurable)
   - High-quality, natural voice

4. **Voice Activity Detection (VAD):** Silero VAD
   - Detects when user starts/stops speaking
   - Reduces latency and false triggers

## Key Differences from Agent 1

| Feature | Agent 1 (Realtime) | Agent 2 (Standard) |
|---------|-------------------|-------------------|
| Architecture | Realtime Gemini | STT → LLM → TTS |
| STT | Built-in Gemini | OpenAI Whisper |
| LLM | Google Gemini | OpenAI GPT-4 |
| TTS | Google Aoede | ElevenLabs |
| Vision | ✅ Yes | ❌ No |
| Latency | <200ms | ~500-1000ms |
| Cost | Lower | Higher |
| Customization | Limited voice | Many voices |

## Environment Variables Required

```env
# OpenAI (for Whisper STT and GPT-4 LLM)
OPENAI_API_KEY=your-openai-api-key

# ElevenLabs (for TTS)
ELEVENLABS_API_KEY=your-elevenlabs-api-key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Optional, defaults to Rachel

# LiveKit (same as Agent 1)
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-secret

# Backend API (same as Agent 1)
BACKEND_URL=http://localhost:8000/api
```

## Available ElevenLabs Voices

You can customize the voice by setting `ELEVENLABS_VOICE_ID`:

- **Rachel** (default): `21m00Tcm4TlvDq8ikWAM` - Warm, friendly female
- **Antoni**: `ErXwobaYiN019PkySvjV` - Well-rounded male
- **Bella**: `EXAVITQu4vr4xnSDxMaL` - Soft, gentle female
- **Josh**: `TxGEqnHWrfWFTfGW9XjX` - Deep, authoritative male
- **Elli**: `MF3mGyEYCl7XYWbV9V6O` - Young, energetic female
- **Dorothy**: `ThT5KcBeYPX3keUQqHPh` - Pleasant, mature female

## Installation

No additional installation needed! Uses existing dependencies from main project:

```bash
# Already in requirements.txt
livekit-agents[openai]
livekit-plugins-silero
livekit-plugins-elevenlabs
```

## Running Agent 2

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run agent 2
cd agent2
python agent.py dev
```

### Production Mode

```bash
# Run as production worker
python agent.py start
```

### Using VS Code Task

Use the predefined task: **"Start Agent 2 - Transcript Agent"**

## How It Works

### 1. Initialization
- Agent connects to LiveKit room
- Sets up STT/LLM/TTS pipeline
- Loads function tools (update_display, etc.)
- Waits silently for activation

### 2. Activation
- User says "mirror mirror"
- Speech detected by Silero VAD
- Transcribed by Whisper
- GPT-4 recognizes activation phrase
- Calls `start_session()` function
- Responds with greeting

### 3. Conversation
- VAD detects user speech
- Whisper transcribes to text
- GPT-4 generates response
- Can call functions (update_display, etc.)
- ElevenLabs synthesizes speech
- Audio played to user

### 4. Session End
- User says goodbye
- GPT-4 calls `close_session()`
- Mirror resets
- Agent returns to listening state

## Function Tools

Agent 2 uses the same function tools as Agent 1:

1. **start_session()** - Activate mirror with sound
2. **update_display(text)** - Update mirror text display
3. **display_speech(content)** - Show speech on mirror
4. **close_session()** - End session and reset

## Advantages of Standard Pipeline

1. **Flexibility**: Easy to swap STT/LLM/TTS providers
2. **Debugging**: Clear separation of components
3. **Voice Options**: Many ElevenLabs voices available
4. **Proven**: Battle-tested pipeline architecture
5. **Control**: More control over each stage

## Disadvantages vs Realtime

1. **Higher Latency**: ~500-1000ms vs <200ms
2. **No Vision**: Cannot see/analyze guest appearance
3. **Higher Cost**: OpenAI + ElevenLabs pricing
4. **More Complex**: Multiple service dependencies

## Performance Tuning

### Reduce Latency
```python
# Use faster models
tts=elevenlabs.TTS(
    model="eleven_turbo_v2",  # Faster turbo model
    latency=1,  # Optimize for latency
)

llm=openai.LLM(
    model="gpt-4o-mini",  # Faster, cheaper model
)
```

### Improve Quality
```python
# Use higher quality models
tts=elevenlabs.TTS(
    model="eleven_multilingual_v2",  # Better quality
)

llm=openai.LLM(
    model="gpt-4o",  # Best reasoning
    temperature=0.8,  # More creative
)
```

## Cost Comparison (per 3-min conversation)

| Service | Cost |
|---------|------|
| Whisper STT | ~$0.006 |
| GPT-4o LLM | ~$0.02-0.05 |
| ElevenLabs TTS | ~$0.15-0.30 |
| **Total** | **~$0.18-0.36** |

vs Agent 1 (Gemini Realtime): ~$0.05-0.10

## Monitoring & Debugging

### Enable Debug Logging
```python
logging.basicConfig(level=logging.DEBUG)
```

### Monitor Pipeline Events
```python
@assistant.on("user_started_speaking")
def on_user_started():
    logger.info("User started speaking")

@assistant.on("user_stopped_speaking")
def on_user_stopped():
    logger.info("User stopped speaking")

@assistant.on("agent_started_speaking")
def on_agent_started():
    logger.info("Agent started speaking")
```

## Troubleshooting

### Issue: Agent doesn't activate
- Check logs for "mirror mirror" detection
- Verify microphone permissions
- Test Whisper transcription accuracy

### Issue: Poor voice quality
- Try different ElevenLabs voice IDs
- Check internet bandwidth
- Verify ElevenLabs API quota

### Issue: High latency
- Switch to turbo models (see Performance Tuning)
- Check network latency to APIs
- Consider using GPT-4o-mini

### Issue: Function calls not working
- Verify tools registered in `fnc_ctx`
- Check function signatures match expectations
- Enable debug logging for LLM calls

## Future Enhancements

- [ ] Add vision support with GPT-4V
- [ ] Implement emotion detection
- [ ] Add background music control
- [ ] Multi-language auto-detection
- [ ] Voice cloning for couple
- [ ] Custom ElevenLabs voice training

## Contributing

This is Agent 2 of the Wedding Mirror project. For questions or improvements, refer to the main project documentation.

## License

Same as main Wedding Mirror project.
