"""
Transcript Agent for Wedding Mirror

This agent joins the same room as the main wedding mirror agent and provides
speech-to-text transcription using Whisper. It listens to conversations and
publishes transcripts to the room for other components to use.
"""

import logging
import asyncio
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
    WorkerOptions,
    cli,
)
from livekit.plugins import openai, noise_cancellation

logger = logging.getLogger("transcript-agent")
load_dotenv()


class TranscriptAgent(Agent):
    def __init__(self, ctx: JobContext) -> None:
        self.ctx = ctx
        self.is_listening = False
        
        # Initialize parent - no tools needed for transcript agent
        super().__init__(
            instructions="You are a silent transcript agent. Listen and transcribe only.",
            llm=None,  # No LLM needed
            tools=[],
        )

    async def on_enter(self):
        print("[TRANSCRIPT AGENT] Joining room for speech-to-text transcription")
        logger.info("Transcript agent entering room")
        self.is_listening = True

    async def on_user_speech(self, speech_text: str, participant_identity: str):
        """Called when speech is transcribed"""
        if not self.is_listening:
            return
            
        print(f"[TRANSCRIPT] {participant_identity}: {speech_text}")
        
        # Publish transcription to the room
        try:
            transcript_data = {
                'type': 'transcription',
                'text': speech_text,
                'participantIdentity': participant_identity,
                'timestamp': int(asyncio.get_event_loop().time() * 1000),
                'isFinal': True
            }
            
            # Publish as data message to the room
            await self.ctx.room.local_participant.publish_data(
                json.dumps(transcript_data).encode('utf-8'),
                topic='transcription'
            )
            print(f"[TRANSCRIPT PUBLISHED] {participant_identity}: {speech_text}")
            
        except Exception as e:
            print(f"[TRANSCRIPT ERROR] Failed to publish: {e}")
            logger.error(f"Failed to publish transcript: {e}")

    async def conversation_item_added(self, item):
        """Handle conversation items for transcription"""
        try:
            if hasattr(item, 'role') and item.role == 'user':
                text = item.content if hasattr(item, 'content') else str(item)
                participant_id = getattr(item, 'participant_identity', 'Guest')
                await self.on_user_speech(text, participant_id)
                
        except Exception as e:
            print(f"[TRANSCRIPT ERROR] Error in conversation_item_added: {e}")
            logger.error(f"Error processing conversation item: {e}", exc_info=True)


async def entrypoint(ctx: JobContext):
    logger.info(f"Transcript agent starting, connecting to room: {ctx.room.name if ctx.room else 'None'}")
    await ctx.connect()
    logger.info(f"Transcript agent connected to room: {ctx.room.name}")
    
    # Create transcript agent
    agent = TranscriptAgent(ctx)
    
    session = AgentSession()
    logger.info("Starting transcript agent session...")
    
    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            video_enabled=False,  # Don't need video for transcription
            audio_enabled=True,   # Need audio for speech-to-text
            noise_cancellation=noise_cancellation.BVC(),
        ),
        # Use Whisper for speech-to-text
        stt=openai.STT(
            model="whisper-1",
            language="en",
        ),
    )
    
    logger.info("Transcript agent session started successfully with Whisper STT")


if __name__ == "__main__":
    # Run transcript agent on a different port/worker
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        # Use different port to avoid conflict with main agent
        port=8081,
    ))