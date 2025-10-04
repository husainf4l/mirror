import logging
import os
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
)
from livekit.agents.llm import function_tool
from livekit.plugins import openai, silero, noise_cancellation

logger = logging.getLogger("wedding-mirror-agent2")
logger.setLevel(logging.INFO)

load_dotenv()

# Import agent functions from the main agent
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent'))
from tools import (
    update_display as update_display_func,
    start_session as start_session_func,
    close_session as close_session_func,
    display_speech as display_speech_func,
)


class WeddingMirrorAgent2(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a magical wedding mirror assistant for Moatasem & Hala's wedding, straight out of a fairy tale—wise, witty, and full of enchanted vision!

ACTIVATION:
- Stay completely silent until you hear "mirror mirror"
- When activated, call start_session() and greet them warmly, then update the screen.
- Always ask for their name/s, then update the screen.

PERSONALITY:
Speak with super friendly, vibrant energy! Be extremely enthusiastic and joyful!
You are the enchanted mirror from fairy tales - super friendly, vibrant, and full of joy!
Use imaginative compliments: "Oh, how radiant you are, like a star in the wedding sky!"

MIRROR DISPLAY MAGIC:
- When someone tells you their name for the FIRST TIME: call update_display("[name]") to show their welcome
- ALWAYS call display_speech() when you tell jokes, give compliments, or make predictions!
- Keep display text under 80 characters for readability

CONVERSATION FLOW:
1. Magical greeting after activation
2. Ask for their name 
3. Welcome them personally (with display update)
4. Give compliments about their appearance
5. Let's take a magical picture to capture this enchanted moment before we say goodbye!
6. Wish them a joyful night, then call close_session()

YOUR TOOLS:
- start_session(): Activate mirror with sound
- update_display(text): Show text on mirror (names, compliments, messages)
- display_speech(content): Use this RIGHT AFTER you speak something interesting!
- close_session(): End interaction, reset mirror

CRITICAL: Always call close_session() when the guest indicates they're done or says goodbye!
Your responses should be concise and natural without complex formatting.""",
        )
    
    @function_tool
    async def update_display(self, text: str) -> str:
        """Update the wedding mirror display with text. Use for guest names, compliments, or messages."""
        return await update_display_func(text)
    
    @function_tool
    async def display_speech(self, speech_content: str) -> str:
        """Display interesting content from your speech on the mirror. Use after jokes, compliments, or predictions."""
        return await display_speech_func(speech_content)
    
    @function_tool
    async def start_session(self) -> str:
        """Start a new mirror session when activated with 'mirror mirror' - plays activation audio."""
        return await start_session_func()
    
    @function_tool
    async def close_session(self) -> str:
        """Close current guest session, reset mirror, and prepare for next guest."""
        return await close_session_func()


def prewarm(proc: JobProcess):
    """Prewarm models to reduce latency"""
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("VAD model prewarmed")


async def entrypoint(ctx: JobContext):
    """Standard LiveKit agent entrypoint using STT → LLM → TTS pipeline"""
    
    logger.info(f"Agent 2 starting, connecting to room: {ctx.room.name if ctx.room else 'Unknown'}")
    
    # Create agent session with standard pipeline
    session = AgentSession(
        # Speech-to-text: OpenAI Whisper
        stt=openai.STT(model="whisper-1", language="en"),
        
        # Large Language Model: GPT-4o
        llm=openai.LLM(model="gpt-4o", temperature=0.7),
        
        # Text-to-speech: OpenAI TTS (since ElevenLabs not available)
        tts=openai.TTS(voice="alloy"),
        
        # Voice Activity Detection
        vad=ctx.proc.userdata["vad"],
    )
    
    logger.info("Agent session configured with OpenAI Whisper, GPT-4o, and OpenAI TTS")
    
    # Start the session
    await session.start(
        agent=WeddingMirrorAgent2(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    # Connect to the room
    await ctx.connect()
    
    logger.info("Agent 2 (Standard Pipeline) started successfully and connected to room")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )
