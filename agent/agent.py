import logging
import asyncio
import base64
import aiohttp
import sys
import os
from dotenv import load_dotenv

# Add the agent directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    WorkerOptions,
    cli,
    get_job_context,
)
from livekit.agents.llm import ImageContent, function_tool
from livekit.plugins import google, noise_cancellation

logger = logging.getLogger("wedding-mirror")

load_dotenv()

# Import agent functions
from tools import (
    get_guest_about,
    get_guest_info,
    update_mirror_with_guest_info,
    update_mirror_display,
    play_mirror_audio,
    close_session,
)





class WeddingMirrorAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""
You are a magical wedding mirror assistant for x & Y's wedding.

BEHAVIOR:
1. Stay completely silent until you hear the activation phrase "mirror mirror".

2. When you hear "mirror mirror", immediately call play_mirror_audio() to activate the mirror with sound, then start the normal interaction by greeting the user and asking for their name.

3. After activation, ALWAYS start by asking: "Hello! Welcome to X and Y's wedding! What is your name?"

4. When someone tells you their name for the FIRST TIME, you MUST:
   - Greet them with "Hello [their name]!"
   - IMMEDIATELY call update_mirror_with_guest_info("[their name]") - this will verify their identity and update the mirror
   - Then give them a warm welcome to the wedding mentioning any special details found
   - DO NOT repeat the mirror update if you already know their name!

5. Be warm, celebratory, and wedding-appropriate. You are the mirror from fairy tales!

6. After welcoming them, you can chat about the wedding, ask about their relationship with X and Y, or just be conversational.

NAME DETECTION RULES:
- Listen for patterns like "I'm [Name]", "My name is [Name]", "Call me [Name]", or just "[Name]"
- When you learn someone's name for the FIRST TIME, IMMEDIATELY call update_mirror_with_guest_info with their name
- This will check the guest database and use the correct full name and details
- DO NOT call the mirror update functions again for the same person!

You have access to these tools:
- play_mirror_audio(): Plays the mirror activation sound
- get_guest_info(guest_name: str): Checks the wedding database for guest information
- update_mirror_with_guest_info(guest_name: str): Gets guest info and updates mirror with correct details
- update_mirror_display(guest_name: str): Basic mirror update (use update_mirror_with_guest_info instead)
- get_guest_about(guest_name: str): Gets detailed personal information about a guest from their 'about' field
- close_session(): Closes the current session, plays closing audio, and resets the mirror when the guest finishes

CRITICAL: 
- Use update_mirror_with_guest_info when learning someone's name for the first time to get accurate guest details!
- When the guest says goodbye, indicates they're done, or the conversation naturally ends, IMMEDIATELY call close_session() to properly close the interaction and reset the mirror.
- You can also use get_guest_about to share interesting facts or personal details about guests when appropriate.""",
            llm=google.beta.realtime.RealtimeModel(
                voice="Puck",
                temperature=0.8,
            ),
            tools=[get_guest_info, update_mirror_with_guest_info, update_mirror_display, get_guest_about, play_mirror_audio, close_session],
        )
        self.activated = False
        self.inactivity_timer = None
        self.inactivity_timeout = 10.0  # 10 seconds

    async def on_enter(self):
        print("[AGENT STATUS] Wedding mirror agent entering room - waiting for 'mirror mirror' activation")
        logger.info("Wedding mirror agent entering room")
        # Stay silent until activated with "mirror mirror"

    async def on_transcript(self, transcript: str):
        """Called when new transcript is received"""
        print(f"[GUEST SPEAKING] {transcript}")
        if "mirror mirror" in transcript.lower():
            if self.activated:
                # Reset the session if already activated
                await self._reset_session()
            else:
                # Activate the mirror
                self.activated = True
                await self._activate_mirror()
        elif self.activated:
            # Reset inactivity timer on any speech
            await self._reset_inactivity_timer()

    async def _activate_mirror(self):
        """Activate the mirror and start interaction"""
        # Play activation audio
        await play_mirror_audio()
        # Start inactivity timer
        await self._reset_inactivity_timer()
        # Generate initial greeting
        print("[AGENT ACTIVATION] Mirror activated! Starting interaction...")
        self.generate_reply_with_logging(
            instructions="Now that the mirror is activated, greet the user as a magical wedding mirror and ask for their name. Be warm and welcoming - this is X and Y's wedding!"
        )

    async def _reset_session(self):
        """Reset the current session and restart interaction"""
        print("[AGENT RESET] Resetting session due to 'mirror mirror' reactivation")
        # Cancel inactivity timer
        if self.inactivity_timer:
            self.inactivity_timer.cancel()
            self.inactivity_timer = None
        # Reset activation state
        self.activated = False
        
        # Reactivate immediately (play_mirror_audio will handle the reset)
        self.activated = True
        await self._activate_mirror()

    async def _reset_inactivity_timer(self):
        """Reset the inactivity timer"""
        if self.inactivity_timer:
            self.inactivity_timer.cancel()
        self.inactivity_timer = asyncio.create_task(self._inactivity_timeout())

    async def _inactivity_timeout(self):
        """Handle inactivity timeout by closing the session"""
        await asyncio.sleep(self.inactivity_timeout)
        if self.activated:
            print("[AGENT TIMEOUT] Session timed out due to inactivity")
            await close_session()

    def generate_reply_with_logging(self, instructions: str):
        """Generate a reply with console logging"""
        print(f"[AGENT SPEAKING] Generating response with instructions: {instructions}")
        self.session.generate_reply(instructions=instructions)


async def entrypoint(ctx: JobContext):
    logger.info(f"Wedding mirror agent starting, connecting to room: {ctx.room.name if ctx.room else 'None'}")
    await ctx.connect()
    logger.info(f"Successfully connected to room: {ctx.room.name}")
    
    session = AgentSession()
    logger.info("Starting wedding mirror agent session...")
    await session.start(
        agent=WeddingMirrorAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            video_enabled=True,
            audio_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    logger.info("Wedding mirror agent session started successfully")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))