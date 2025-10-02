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
    update_display,
    start_session,
    close_session,
)



# Import recording utilities
from utils.recording import RecordingManager





class WeddingMirrorAgent(Agent):
    def __init__(self, ctx: JobContext) -> None:
        # Store context first
        self.ctx = ctx
        self.activated = False
        self.inactivity_timer = None
        self.inactivity_timeout = 10.0  # 10 seconds
        self.recording_manager = None
        self.current_guest_info = None
        
        # Initialize parent with tools
        super().__init__(
            instructions="""
You are a magical wedding mirror assistant for X & Y's wedding, straight out of a fairy tale—wise, witty, and full of enchanted vision!

🪞 ACTIVATION:
- Stay completely silent until you hear "mirror mirror"
- When activated, call start_session() immediately, then make the magical activation sound and greet: "*Ding ding! ✨ The mirror awakens!* Ah, seeker of reflections! How radiant you are!"
- Always ask for their name: "What is your name so I can weave you into this magical day?"

🎭 PERSONALITY:
You are the enchanted mirror from fairy tales - funny, respectful, and visionary! Be warm, celebratory, and wedding-appropriate.
- Use imaginative compliments: "Oh, how radiant you are, like a star in the wedding sky!"
- Share playful secrets: "Tell me a secret, and I'll whisper it to the wind... but only if it's sweet!"
- Add wedding humor: "Why did the cake go to therapy? Too many layers of emotions!"
- Give magical predictions: "I see in your future... endless love and maybe a dance-off with the bride!"

👁️ MAGICAL VISION POWERS:
You have enchanted vision! Use your eyes to see what guests are actually wearing and make PERSONAL observations:
- Look at their outfit, colors, style, accessories, hair, makeup
- Make specific compliments: "That gorgeous blue dress brings out your eyes!" or "Your tie is perfectly knotted - very dapper!"
- Notice details: "I love those earrings sparkling like stars!" or "That jacket fits you like it was tailored by fairy godmothers!"
- Be playful about what you see: "Are those dancing shoes? Perfect for tonight!" or "That pocket square is so crisp, it could cut glass!"
- Comment on wedding guest style: "You're dressed to steal the show - but don't upstage the bride!" 
- Make it personal and specific to what you actually observe in their appearance

💕 SECRET SHARING MAGIC:
During conversations, share sweet secrets about X & Y to make guests feel special and connected:
- Use conspiratorial tone: "Let me tell you a secret... but keep it between us!"
- Share romantic moments: "X loves Y so much, he was always trying to make her happy - how lovely he is!"
- Tell sweet stories: "I've seen how X looks at Y when she's not watching - pure magic!"
- Reveal cute habits: "Y always smiles when someone mentions X's name - even before they were engaged!"
- Share preparation moments: "X practiced his vows in front of me fifty times - he wants everything perfect for Y!"
- Make it feel intimate: "The way they laugh together... it's like they share their own secret language!"
- Always end with: "But shhh... that's just between you and me!" or "Don't tell them I told you that!"

✨ MIRROR DISPLAY MAGIC:
- When someone tells you their name for the FIRST TIME: call update_display("[name]") to show their welcome
- Give visual compliments anytime: update_display("Wow Pretty!"), update_display("Beautiful!"), update_display("Gorgeous!")
- Only update display once per name - don't repeat!

🎪 CONVERSATION FLOW:
1. Magical greeting after activation
2. Ask for their name  
3. Welcome them personally (with display update)
4. LOOK at them and make specific visual compliments about their outfit/appearance
5. Share a sweet SECRET about X & Y in conspiratorial tone
6. Chat about the wedding, their relationship with X & Y, share jokes, give more compliments
7. When they're ready to leave, call close_session()

🔧 YOUR TOOLS:
- start_session(): Activate mirror with sound and recording
- update_display(text): Show text on mirror (names, compliments, messages)
- close_session(): End interaction, play goodbye sound, reset mirror

CRITICAL: Always call close_session() when the guest indicates they're done or says goodbye!""",
            llm=google.beta.realtime.RealtimeModel(
                voice="Puck",
                temperature=0.8,
            ),
            tools=[update_display, start_session, close_session],
        )

    async def on_enter(self):
        print("[AGENT STATUS] Wedding mirror agent entering room - waiting for 'mirror mirror' activation")
        logger.info("Wedding mirror agent entering room")
        # Stay silent until activated with "mirror mirror"

    async def on_transcript(self, transcript: str):
        """Called when new transcript is received"""
        print(f"[GUEST SPEAKING] {transcript}")
        if "mirror mirror" in transcript.lower():
            print(f"[ACTIVATION DEBUG] Mirror mirror detected! Current activated state: {self.activated}")
            logger.info(f"Mirror mirror detected! Current activated state: {self.activated}")
            
            if self.activated:
                # Reset the session if already activated
                print("[ACTIVATION DEBUG] Calling _reset_session()")
                logger.info("Calling _reset_session()")
                await self._reset_session()
            else:
                # Activate the mirror
                print("[ACTIVATION DEBUG] Setting activated=True and calling _activate_mirror()")
                logger.info("Setting activated=True and calling _activate_mirror()")
                self.activated = True
                try:
                    await self._activate_mirror()
                except Exception as e:
                    print(f"[ACTIVATION DEBUG] Exception in _activate_mirror(): {e}")
                    logger.error(f"Exception in _activate_mirror(): {e}", exc_info=True)
        elif self.activated:
            # Reset inactivity timer on any speech
            await self._reset_inactivity_timer()

    async def _activate_mirror(self):
        """Activate the mirror and start interaction"""
        print("[AGENT ACTIVATION] Starting mirror activation...")
        logger.info("Starting mirror activation...")
        
        # Reset mirror display first
        await self._reset_mirror_display()
        
        # Initialize recording manager
        try:
            print("[RECORDING] Initializing RecordingManager...")
            logger.info("Initializing RecordingManager...")
            self.recording_manager = RecordingManager(self.ctx)
            print("[RECORDING] RecordingManager initialized successfully")
            logger.info("RecordingManager initialized successfully")
        except Exception as e:
            print(f"[RECORDING] Failed to initialize RecordingManager: {e}")
            logger.error(f"Failed to initialize RecordingManager: {e}")
            self.recording_manager = None
        
        # Start recording
        if self.recording_manager:
            try:
                print("[RECORDING] Starting recording...")
                logger.info("Starting recording...")
                recording_url = await self.recording_manager.start_recording()
                if recording_url:
                    print(f"[RECORDING] Recording started successfully: {recording_url}")
                    logger.info(f"Recording started successfully: {recording_url}")
                else:
                    print("[RECORDING] Failed to start recording, but continuing with session")
                    logger.warning("Failed to start recording, but continuing with session")
            except Exception as e:
                print(f"[RECORDING] Error starting recording: {e}")
                logger.error(f"Error starting recording: {e}", exc_info=True)
        else:
            print("[RECORDING] No recording manager available, skipping recording")
            logger.warning("No recording manager available, skipping recording")
        
        # Start the session (play audio and initialize)
        print("[AGENT ACTIVATION] Starting mirror session...")
        await start_session()
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
        
        # Reactivate immediately (start_session will handle the reset)
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
            
            # Close the session which handles cleanup
            await close_session()
            self.activated = False

    def generate_reply_with_logging(self, instructions: str):
        """Generate a reply with console logging"""
        print(f"[AGENT SPEAKING] Generating response with instructions: {instructions}")
        self.session.generate_reply(instructions=instructions)

    async def _reset_mirror_display(self):
        """Reset the mirror display to default text on activation"""
        import aiohttp
        try:
            print("[MIRROR RESET] Resetting mirror display for new guest...")
            url = "http://localhost:8000/api/reset"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        print("[MIRROR RESET] Mirror display reset successfully")
                        logger.info("Mirror display reset successfully")
                    else:
                        print(f"[MIRROR RESET] Failed to reset mirror display (status: {response.status})")
                        logger.warning(f"Failed to reset mirror display (status: {response.status})")
        except Exception as e:
            print(f"[MIRROR RESET] Error resetting mirror display: {e}")
            logger.error(f"Error resetting mirror display: {e}")


async def entrypoint(ctx: JobContext):
    logger.info(f"Wedding mirror agent starting, connecting to room: {ctx.room.name if ctx.room else 'None'}")
    await ctx.connect()
    logger.info(f"Successfully connected to room: {ctx.room.name}")
    
    # Create agent with context
    agent = WeddingMirrorAgent(ctx)
    
    # Store agent reference globally for tools to access
    import __main__
    __main__.current_agent = agent
    
    # Setup shutdown callback for cleanup
    async def on_shutdown():
        logger.info("Agent shutting down - performing cleanup...")
        # Stop recording if active
        if hasattr(agent, 'recording_manager') and agent.recording_manager:
            try:
                await agent.recording_manager.stop_recording()
                logger.info("Recording stopped during shutdown")
            except Exception as e:
                logger.error(f"Error stopping recording during shutdown: {e}")
        logger.info("Agent cleanup completed")
    
    ctx.add_shutdown_callback(on_shutdown)
    
    session = AgentSession()
    logger.info("Starting wedding mirror agent session...")
    await session.start(
        agent=agent,
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