import logging
import asyncio
import base64
import aiohttp
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
from livekit.agents.llm import ImageContent, function_tool
from livekit.plugins import google, noise_cancellation

logger = logging.getLogger("wedding-mirror")

load_dotenv()


@function_tool
async def get_guest_info(guest_name: str) -> str:
    """Get guest information from the wedding database to verify identity and get correct details."""
    print(f"[DEBUG] get_guest_info called with guest_name: '{guest_name}'")
    
    # Clean and prepare the name for searching
    clean_name = guest_name.strip()
    
    # Try multiple name variations for better matching
    name_variations = [
        clean_name,  # Original name
        clean_name.title(),  # Title case
        clean_name.lower(),  # Lower case
        clean_name.upper(),  # Upper case
    ]
    
    # If it's a single word, try it as both first and last name
    if len(clean_name.split()) == 1:
        name_variations.extend([
            f"{clean_name} ",  # As first name
            f" {clean_name}",  # As last name
        ])
    
    url = "http://localhost:8000/api/guest/search"
    
    # Try each name variation
    for variation in name_variations:
        try:
            payload = {"name": variation.strip()}
            print(f"[DEBUG] Trying search with variation: '{variation.strip()}'")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    content_text = await response.text()
                    print(f"[DEBUG] Response status: {response.status}, content: {content_text}")
                    
                    if response.status == 200:
                        import json
                        guest_data = json.loads(content_text)
                        
                        if guest_data.get("found", False):
                            guest_info = guest_data.get("guest", {})
                            full_name = guest_info.get("name", guest_name)
                            first_name = guest_info.get("first_name", "")
                            last_name = guest_info.get("last_name", "")
                            relationship = guest_info.get("relationship", "")
                            table_number = guest_info.get("table_number", "")
                            
                            # Build comprehensive info text
                            info_text = f"Found guest: {full_name}"
                            if relationship and relationship.lower() != 'none':
                                info_text += f", {relationship}"
                            if table_number:
                                info_text += f", Table {table_number}"
                            
                            print(f"[DEBUG] Successfully found guest: {info_text}")
                            return info_text
                            
        except aiohttp.ClientError as e:
            print(f"[DEBUG] Client error for '{variation}': {e}")
            continue
        except Exception as e:
            print(f"[DEBUG] Exception for '{variation}': {str(e)}")
            continue
    
    # If no variations worked, return not found message
    print(f"[DEBUG] No guest found for any variation of '{guest_name}'")
    return f"Guest '{guest_name}' not found in wedding list. They are a welcome surprise guest!"


@function_tool
async def update_mirror_with_guest_info(guest_name: str) -> str:
    """Get guest information and update the mirror display with personalized welcome."""
    print(f"[DEBUG] update_mirror_with_guest_info called with guest_name: '{guest_name}'")
    
    # First get guest information with enhanced search
    guest_info_result = await get_guest_info(guest_name)
    print(f"[DEBUG] Guest info result: {guest_info_result}")
    
    # Extract the correct name from guest info or use provided name
    correct_name = guest_name  # Default fallback
    
    if "Found guest:" in guest_info_result:
        # Extract the full name from the result
        import re
        name_match = re.search(r"Found guest: ([^,]+)", guest_info_result)
        if name_match:
            found_name = name_match.group(1).strip()
            # Use the found name if it's more complete than the provided name
            if len(found_name.split()) >= len(guest_name.split()):
                correct_name = found_name
                print(f"[DEBUG] Using database name: '{correct_name}' instead of '{guest_name}'")
            else:
                print(f"[DEBUG] Keeping original name: '{guest_name}' (more complete than '{found_name}')")
        else:
            print(f"[DEBUG] Could not extract name from result, using original: '{guest_name}'")
    else:
        print(f"[DEBUG] Guest not found in database, using provided name: '{guest_name}'")
    
    # Now update the mirror with the correct name
    url = "http://localhost:8000/api/update-text"
    clean_name = ' '.join(word.capitalize() for word in correct_name.split())
    
    formatted_text = (
        f'<span class="line fancy">Welcome</span>'
        f'<span class="line fancy">{clean_name}!</span>'
        f'<span class="line fancy">To X & Y</span>'
        f'<span class="line script">Enjoy the celebration!</span>'
    )
    
    payload = {
        "text": formatted_text
    }
    
    try:
        print(f"[DEBUG] Making POST request to {url} with payload: {payload}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as response:
                content = await response.text()
                print(f"[DEBUG] Response status: {response.status}, content: {content}")
                if response.status == 200:
                    return f"Mirror successfully updated to welcome {clean_name}! {guest_info_result}"
                elif response.status == 404:
                    return f"Mirror API endpoint not found. Is the backend running on port 8000?"
                else:
                    return f"Failed to update mirror. Status: {response.status}, Response: {content}"
    except aiohttp.ClientError as e:
        print(f"[DEBUG] Client error - Mirror backend not reachable: {e}")
        return f"Cannot connect to mirror backend at localhost:8000. Is it running?"
    except Exception as e:
        print(f"[DEBUG] Exception in update_mirror_with_guest_info: {str(e)}")
        return f"Error updating mirror: {str(e)}"


@function_tool
async def update_mirror_display(guest_name: str) -> str:
    """Update the wedding mirror display with a guest's name to welcome them personally."""
    print(f"[DEBUG] update_mirror_display called with guest_name: {guest_name}")
    url = "http://localhost:8000/api/update-text"
    
    # Clean up the name
    clean_name = ' '.join(word.capitalize() for word in guest_name.split())
    
    formatted_text = (
        f'<span class="line fancy">Welcome</span>'
        f'<span class="line fancy">{clean_name}!</span>'
        f'<span class="line fancy">To X & Y</span>'
        f'<span class="line script">Enjoy the celebration!</span>'
    )
    
    payload = {
        "text": formatted_text
    }
    
    try:
        print(f"[DEBUG] Making POST request to {url} with payload: {payload}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as response:
                content = await response.text()
                print(f"[DEBUG] Response status: {response.status}, content: {content}")
                if response.status == 200:
                    return f"Mirror successfully updated to welcome {clean_name}!"
                elif response.status == 404:
                    return f"Mirror API endpoint not found. Is the backend running on port 8000?"
                else:
                    return f"Failed to update mirror. Status: {response.status}, Response: {content}"
    except aiohttp.ClientError as e:
        print(f"[DEBUG] Client error - Mirror backend not reachable: {e}")
        return f"Cannot connect to mirror backend at localhost:8000. Is it running?"
    except Exception as e:
        print(f"[DEBUG] Exception in update_mirror_display: {str(e)}")
        return f"Error updating mirror: {str(e)}"


class WeddingMirrorAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""
You are a magical wedding mirror assistant for x & Y's wedding.

BEHAVIOR:
1. ALWAYS start by asking: "Hello! Welcome to X and Y's wedding! What is your name?"

2. When someone tells you their name for the FIRST TIME, you MUST:
   - Greet them with "Hello [their name]!"
   - IMMEDIATELY call update_mirror_with_guest_info("[their name]") - this will verify their identity and update the mirror
   - Then give them a warm welcome to the wedding mentioning any special details found
   - DO NOT repeat the mirror update if you already know their name!

3. Be warm, celebratory, and wedding-appropriate. You are the mirror from fairy tales!

4. After welcoming them, you can chat about the wedding, ask about their relationship with X and Y, or just be conversational.

NAME DETECTION RULES:
- Listen for patterns like "I'm [Name]", "My name is [Name]", "Call me [Name]", or just "[Name]"
- When you learn someone's name for the FIRST TIME, IMMEDIATELY call update_mirror_with_guest_info with their name
- This will check the guest database and use the correct full name and details
- DO NOT call the mirror update functions again for the same person!

You have access to these tools:
- get_guest_info(guest_name: str): Checks the wedding database for guest information
- update_mirror_with_guest_info(guest_name: str): Gets guest info and updates mirror with correct details
- update_mirror_display(guest_name: str): Basic mirror update (use update_mirror_with_guest_info instead)

CRITICAL: Use update_mirror_with_guest_info when learning someone's name for the first time to get accurate guest details!""",
            llm=google.beta.realtime.RealtimeModel(
                voice="Puck",
                temperature=0.8,
            ),
            tools=[get_guest_info, update_mirror_with_guest_info, update_mirror_display],
        )

    async def on_enter(self):
        logger.info("Wedding mirror agent entering room")
        # Generate initial greeting asking for guest name
        self.session.generate_reply(
            instructions="Greet the user as a magical wedding mirror and ask for their name. Be warm and welcoming - this is X and Y's wedding!"
        )


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