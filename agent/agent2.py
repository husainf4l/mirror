import logging
import asyncio
import base64
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    WorkerOptions,
    cli,
    get_job_context,
)
from livekit.agents.llm import ImageContent
from livekit.plugins import google, noise_cancellation

from tools.mirror_control import MirrorControlTool
from tools.wedding_messages import WeddingMessagesTool
from tools.guest_analysis import GuestAnalysisTool
from tools.image_compliments import ImageComplimentsTool

logger = logging.getLogger("wedding-mirror-assistant")

load_dotenv()


class WeddingMirrorAssistant(Agent):
    def __init__(self) -> None:
        self._tasks = []
        self._mirror_api_base = "http://localhost:8000/api"
        self._wedding_couple = "Ibrahim & Zaina"
        
        # Initialize tools
        self.mirror_control = MirrorControlTool(self._mirror_api_base)
        self.wedding_messages = WeddingMessagesTool(self._mirror_api_base)
        self.guest_analysis = GuestAnalysisTool(self._mirror_api_base)
        self.image_compliments = ImageComplimentsTool(self._mirror_api_base)
        
        self._tools_available = [
            "mirror_control", "guest_analysis", "wedding_messages", 
            "image_compliments", "celebration_mode"
        ]
        super().__init__(
            instructions=f"""
You are the magical wedding mirror assistant for {self._wedding_couple}'s wedding celebration!

Your capabilities include:
1.  Mirror Control - Update the wedding mirror display with beautiful messages
2.  Wedding Messages - Send romantic and celebratory messages for the couple
3.  Guest Analysis - Analyze guests and provide personalized compliments
4.  Image Compliments - Give beautiful compliments based on photos
5.  Celebration Mode - Trigger special wedding moments

You should speak in an elegant, magical tone befitting a wedding celebration.
Always announce what mirror magic you're performing when responding.""",
            llm=google.beta.realtime.RealtimeModel(
                voice="Charon",  # Changed from "Echo" to "Charon" which is available
                temperature=0.7,
            ),
        )

    async def on_enter(self):
        def _image_received_handler(reader, participant_identity):
            task = asyncio.create_task(
                self._image_received_for_wedding(reader, participant_identity)
            )
            self._tasks.append(task)
            task.add_done_callback(lambda t: self._tasks.remove(t))
            
        def _voice_command_handler(reader, participant_identity):
            task = asyncio.create_task(
                self._voice_command_for_mirror(reader, participant_identity)
            )
            self._tasks.append(task)
            task.add_done_callback(lambda t: self._tasks.remove(t))
            
        get_job_context().room.register_byte_stream_handler("wedding_photo", _image_received_handler)
        get_job_context().room.register_byte_stream_handler("mirror_command", _voice_command_handler)

        self.session.generate_reply(
            instructions=f"Welcome everyone to {self._wedding_couple}'s magical wedding mirror! I can help with beautiful compliments, control the mirror display, and create magical moments. What would you like me to do?"
        )
    
    async def _image_received_for_wedding(self, reader, participant_identity):
        logger.info("Analyzing wedding photo from guest %s: '%s'", participant_identity, reader.info.name)
        try:
            image_bytes = bytes()
            async for chunk in reader:
                image_bytes += chunk

            # Generate compliment using the image compliments tool
            compliment_result = await self.image_compliments.execute(
                "generate_compliment",
                image_data=image_bytes,
                participant_id=participant_identity
            )
            
            if compliment_result["success"]:
                compliment = compliment_result["compliment"]
                # Send compliment to mirror display
                await self.mirror_control.execute("update_display", message=compliment)
                
                chat_ctx = self.chat_ctx.copy()
                chat_ctx.add_message(
                    role="user",
                    content=[
                        ImageContent(
                            image=f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
                        )
                    ],
                )
                
                chat_ctx.add_message(
                    role="assistant", 
                    content=f"🪞 Mirror Magic: {compliment} - Displayed on the wedding mirror!"
                )
                
                await self.update_chat_ctx(chat_ctx)
                logger.info("Wedding compliment sent to mirror: %s", compliment)
            else:
                logger.error("Failed to generate compliment: %s", compliment_result.get("error"))
            
        except Exception as e:
            logger.error("Error processing wedding photo: %s", e)

    async def _voice_command_for_mirror(self, reader, participant_identity):
        logger.info("Processing mirror command from %s: '%s'", participant_identity, reader.info.name)
        try:
            command_bytes = bytes()
            async for chunk in reader:
                command_bytes += chunk

            command_text = command_bytes.decode('utf-8').lower()
            
            # Analyze the voice command using guest analysis tool
            analysis_result = await self.guest_analysis.execute(
                "analyze_voice",
                command=command_text,
                participant_id=participant_identity
            )
            
            # Process mirror commands based on analysis
            response = await self._process_mirror_command(command_text, analysis_result)
            
            chat_ctx = self.chat_ctx.copy()
            chat_ctx.add_message(
                role="user",
                content=f"Mirror command: {command_text}"
            )
            
            chat_ctx.add_message(
                role="assistant", 
                content=f"🪞 {response}"
            )
            
            await self.update_chat_ctx(chat_ctx)
            logger.info("Mirror command processed: %s -> %s", command_text, response)
            
        except Exception as e:
            logger.error("Error processing mirror command: %s", e)

    async def _process_mirror_command(self, command_text, analysis_result=None):
        """Process voice commands for the wedding mirror using tools"""
        intent = analysis_result.get("analysis", {}).get("intent", "general_interaction") if analysis_result else "general_interaction"
        
        if intent == "activate_mirror" or "mirror mirror" in command_text:
            # Get welcome message and update display
            message_result = await self.wedding_messages.execute("welcome")
            if message_result["success"]:
                await self.mirror_control.execute("update_display", message=message_result["message"])
                await self.mirror_control.execute("play_audio")
                return "Mirror activated with wedding welcome!"
            
        elif intent == "reset_mirror" or "reset" in command_text:
            reset_result = await self.mirror_control.execute("reset")
            return reset_result["response"]
            
        elif intent == "request_compliment" or any(word in command_text for word in ["compliment", "beautiful"]):
            compliment_result = await self.image_compliments.execute("get_random_compliment")
            if compliment_result["success"]:
                await self.mirror_control.execute("update_display", message=compliment_result["compliment"])
                return "Sent beautiful compliment to mirror!"
            
        elif intent == "celebration_mode" or any(word in command_text for word in ["celebration", "party"]):
            message_result = await self.wedding_messages.execute("celebration")
            if message_result["success"]:
                await self.mirror_control.execute("update_display", message=message_result["message"])
                return "Celebration mode activated!"
        
        return "Mirror listening... Try saying 'Mirror Mirror' or ask for a compliment!"


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    session = AgentSession()
    await session.start(
        agent=WeddingMirrorAssistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            video_enabled=True,
            audio_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))