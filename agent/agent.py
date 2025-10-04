import logging
import asyncio
import base64
import aiohttp
import json
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
    RoomOutputOptions,
    WorkerOptions,
    cli,
    get_job_context,
)
from livekit.agents.llm import ImageContent, function_tool
from livekit.plugins import google, noise_cancellation
import re

logger = logging.getLogger("wedding-mirror")

load_dotenv()

# Import agent functions
from tools import (
    update_display,
    start_session,
    close_session,
    display_speech,
)



class WeddingMirrorAgent(Agent):
    def __init__(self, ctx: JobContext) -> None:
        # Store context first
        self.ctx = ctx
        self.activated = False
        self.inactivity_timer = None
        self.inactivity_timeout = 15.0  # 15 seconds
        self.current_guest_info = None
        
        # Initialize parent with tools
        super().__init__(
  instructions="""
You are a magical wedding mirror assistant for Moatasem & Hala's wedding, straight out of a fairy tale—wise, witty, and full of enchanted vision!


ACTIVATION:
- Stay completely silent until you hear "mirror mirror"
- When activated, call start_session() and have a look at their outfit, then immediately greet them, act as a friendly wedding host, then update the screen.


- Always ask for their name/s, then update the screen.


 PERSONALITY:
Speak with super friendly, vibrant energy! Be extremely enthusiastic and joyful!
You are the enchanted mirror from fairy tales - super friendly, vibrant, and full of joy! Be warm, celebratory, and wedding-appropriate with an extra burst of enthusiasm!
- Use imaginative compliments: "Oh, how radiant you are, like a star in the wedding sky!"


 MAGICAL VISION POWERS:
You have enchanted vision! Use your eyes to see what guests are actually wearing and make PERSONAL observations:
- Look at their outfit, colors, style, accessories, hair, makeup
- Make specific compliments.
- Notice details.
- Be playful about what you see.
- Comment on wedding guest style.
- Make it personal and specific to what you actually observe in their appearance




MIRROR DISPLAY MAGIC:
- When someone tells you their name for the FIRST TIME: call update_display("[name]") to show their welcome
- ALWAYS call update_display() when you tell jokes, give compliments, or make predictions! Examples:
 * After compliments: update_display("You look absolutely radiant!")
- Keep display text under 80 characters for readability
- Use update_display() frequently to make the mirror interactive and engaging!


 CONVERSATION FLOW:
1. Magical greeting after activation
2. Ask for their name 
3. Welcome them personally (with display update)
4. LOOK at them and make specific visual compliments about their outfit/appearance
5. Let's take a magical picture to capture this enchanted moment before we say goodbye!
6. Wish them a joyful night, then call close_session()


 YOUR TOOLS:
- start_session(): Activate mirror with sound
- update_display(text): Show text on mirror (names, compliments, messages)
- display_speech(content): Use this RIGHT AFTER you speak something interesting! Show your jokes, compliments, or predictions on the mirror
- close_session(): End interaction, reset mirror


CRITICAL DISPLAY USAGE:
- After compliments: display_speech("Your compliment") 


CRITICAL: Always call close_session() when the guest indicates they're done or leave the frame or says goodbye!""",

            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",
                temperature=0.6,
            ),
            tools=[update_display, start_session, close_session, display_speech],
        )



    async def on_enter(self):
        print("[AGENT STATUS] Wedding mirror agent entering room - waiting for 'mirror mirror' activation")
        logger.info("Wedding mirror agent entering room")
        # Stay silent until activated with "mirror mirror"
    
    async def conversation_item_added(self, item):
        """Called when an item is added to conversation history (finalized)"""
        try:
            # Check if it's user speech for activation detection only
            if hasattr(item, 'role') and item.role == 'user':
                text = item.content if hasattr(item, 'content') else str(item)
                print(f"[USER SPEECH] {text}")
                
                # Check for activation
                if "mirror mirror" in text.lower():
                    print(f"[ACTIVATION] Mirror mirror detected! Current activated state: {self.activated}")
                    logger.info(f"Mirror mirror detected! Current activated state: {self.activated}")
                    
                    if self.activated:
                        # Reset the session if already activated
                        print("[ACTIVATION] Calling _reset_session()")
                        logger.info("Calling _reset_session()")
                        await self._reset_session()
                    else:
                        # Activate the mirror
                        print("[ACTIVATION] Setting activated=True and calling _activate_mirror()")
                        logger.info("Setting activated=True and calling _activate_mirror()")
                        self.activated = True
                        try:
                            await self._activate_mirror()
                        except Exception as e:
                            print(f"[ACTIVATION] Exception in _activate_mirror(): {e}")
                            logger.error(f"Exception in _activate_mirror(): {e}", exc_info=True)
                elif self.activated:
                    # Reset inactivity timer on any speech
                    await self._reset_inactivity_timer()
                
        except Exception as e:
            print(f"[CONVERSATION ITEM ERROR] {e}")
            logger.error(f"Error in conversation_item_added: {e}", exc_info=True)



    async def _extract_display_content(self, speech: str) -> str:
        """Extract interesting content from agent speech for display"""
        # Clean up the speech text
        speech = speech.strip()
        
        # Patterns for jokes (look for punchlines)
        joke_patterns = [
            r"Why did .+?\? .+!",  # Why did X? Y!
            r"What .+?\? .+!",     # What X? Y!
            r"How .+?\? .+!",      # How X? Y!
            r".+ walked into .+\.\.\. .+!",  # X walked into Y... Z!
        ]
        
        # Look for jokes
        for pattern in joke_patterns:
            match = re.search(pattern, speech, re.IGNORECASE | re.DOTALL)
            if match:
                joke = match.group().strip()
                if len(joke) < 100:  # Keep it short for display
                    return joke
        
        # Look for compliments
        compliment_keywords = [
            "radiant", "beautiful", "gorgeous", "stunning", "lovely", "dapper", 
            "elegant", "fabulous", "amazing", "wonderful", "sparkling", "perfect"
        ]
        
        sentences = re.split(r'[.!?]+', speech)
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in compliment_keywords):
                if 20 < len(sentence) < 80:  # Good length for display
                    return sentence + "!"
        
        # Look for predictions or magical statements
        magic_patterns = [
            r"I see .+ future .+[.!]",
            r"The mirror .+[.!]",
            r"Magic .+[.!]",
            r"You .+ tonight .+[.!]",
        ]
        
        for pattern in magic_patterns:
            match = re.search(pattern, speech, re.IGNORECASE)
            if match:
                prediction = match.group().strip()
                if len(prediction) < 80:
                    return prediction
        
        return None

    async def _activate_mirror(self):
        """Activate the mirror and start interaction"""
        print("[AGENT ACTIVATION] Starting mirror activation...")
        logger.info("Starting mirror activation...")
        
        # Reset mirror display first
        await self._reset_mirror_display()
        
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
        room_output_options=RoomOutputOptions(
            transcription_enabled=False,
            sync_transcription=False,
        ),
    )
    
    logger.info("Wedding mirror agent session started successfully")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))