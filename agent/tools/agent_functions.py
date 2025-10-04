"""
Agent Functio    # Use the provided text directly
    display_text = text.strip()
    
    # Now update the mirror with the textng Mirror

This module contains all the function tools used by the wedding mirror agent.
"""

import asyncio
import aiohttp
import subprocess
from livekit.agents.llm import function_tool


@function_tool
async def update_display(text: str) -> str:
    """Update the wedding mirror display with any text message. Use this to show personalized messages, compliments, guest names, or any other text on the mirror display. For guest names, it will also store the name for recording purposes."""
    print(f"[DEBUG] update_display called with text: '{text}'")
    
    # Use the provided text directly
    display_text = text.strip()
    
    # If this looks like a guest name (single words or names), store for recording purposes
    import __main__
    if hasattr(__main__, 'current_agent') and __main__.current_agent:
        # Check if text looks like a name (not a full sentence)
        if len(display_text.split()) <= 3 and not display_text.endswith(('.', '!', '?')):
            if hasattr(__main__.current_agent, 'recording_manager') and __main__.current_agent.recording_manager:
                __main__.current_agent.recording_manager.guest_name = display_text
    
    # Now update the mirror with the text
    url = "http://localhost:8000/api/update-text"
    
    # Check if this is a name (for welcome format) or general text
    if len(display_text.split()) <= 3 and not any(char in display_text.lower() for char in ['wow', 'pretty', 'beautiful', 'amazing', 'gorgeous']):
        # Format as welcome message for names
        clean_name = display_text.title()
        formatted_text = (
            f'<span class="line fancy">Welcome</span>'
            f'<span class="line fancy">{clean_name}!</span>'
            f'<span class="line fancy">To Moatasem & Hala</span>'
            f'<span class="line script">Enjoy the celebration!</span>'
        )
        display_message = f"Welcome {clean_name}! To Moatasem & Hala - Enjoy the celebration!"
    else:
        # Format as general message for compliments or other text
        formatted_text = (
            f'<span class="line fancy">{display_text}</span>'
            f'<span class="line fancy">To Moatasem & Hala</span>'
            f'<span class="line script">Enjoy the celebration!</span>'
        )
        display_message = f"{display_text} - To Moatasem & Hala - Enjoy the celebration!"

    print(f"[MIRROR DISPLAY] Updating mirror text to: {display_message}")
    
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
                    return f"Mirror successfully updated with: {display_message}"
                elif response.status == 404:
                    return f"Mirror API endpoint not found. Is the backend running on port 8000?"
                else:
                    return f"Failed to update mirror. Status: {response.status}, Response: {content}"
    except aiohttp.ClientError as e:
        print(f"[DEBUG] Client error - Mirror backend not reachable: {e}")
        return f"Cannot connect to mirror backend at localhost:8000. Is it running?"
    except Exception as e:
        print(f"[DEBUG] Exception in update_display: {str(e)}")
        return f"Error updating mirror: {str(e)}"




@function_tool
async def display_speech(speech_content: str) -> str:
    """Display interesting content from your speech on the mirror. Use this after telling jokes, giving compliments, sharing secrets, or making predictions to show the text on the mirror display."""
    print(f"[DISPLAY SPEECH] Showing: {speech_content}")
    
    # Clean and truncate the content for display
    display_text = speech_content.strip()
    if len(display_text) > 80:
        # Try to find a good breaking point
        if '!' in display_text[:80]:
            display_text = display_text[:display_text.find('!', 0, 80) + 1]
        elif '?' in display_text[:80]:
            display_text = display_text[:display_text.find('?', 0, 80) + 1]
        elif '.' in display_text[:80]:
            display_text = display_text[:display_text.find('.', 0, 80) + 1]
        else:
            display_text = display_text[:77] + "..."
    
    # Use the existing update_display function
    return await update_display(display_text)


@function_tool
async def start_session() -> str:
    """Start a new mirror session when activated with 'mirror mirror' - plays activation audio and resets the mirror display."""
    print("[AUDIO] Playing mirror activation sound - Starting new guest session")
    
    # Reset the mirror text to default before playing audio
    try:
        import aiohttp
        url = "http://localhost:8000/api/reset"
        print(f"[MIRROR RESET] Calling API to reset mirror text: {url}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                print(f"[MIRROR RESET] API response status: {response.status}")
                if response.status == 200:
                    print("[MIRROR RESET] Mirror text reset to default successfully")
                else:
                    content = await response.text()
                    print(f"[MIRROR RESET] Failed to reset mirror text (status: {response.status}, content: {content})")
    except Exception as e:
        print(f"[MIRROR RESET] Error resetting mirror text: {e}")
    
    # Return the activation sound for the agent to speak immediately
    print("[AUDIO] Mirror activation completed - returning activation sound...")
    return "*Ding ding! "


@function_tool
async def close_session() -> str:
    """Close current guest session, reset mirror, and prepare for next guest."""
    print("[AGENT ACTION] Closing guest session - resetting mirror")
    
    # Reset the mirror via backend API
    import aiohttp
    try:
        url = "http://localhost:8000/api/reset"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    print("[MIRROR DISPLAY] Mirror reset to default state - ready for next guest")
                    return "✨ *Magical Farewell Chime* 🔮 Farewell, beautiful soul! Until we meet again! *The mirror sleeps...*"
                else:
                    return f"✨ *Magical Farewell Chime* 🔮 Farewell! *The mirror sleeps...* (Mirror reset had issues: {response.status})"
    except Exception as e:
        return f"✨ *Magical Farewell Chime* 🔮 Farewell, beautiful soul! Until we meet again! *The mirror sleeps...* (Reset error: {e})"


@function_tool
async def share_couple_secret() -> str:
    """Share a random, elegant, funny but nice, creative secret about Moatasem and Hala. Use this to delight guests with charming stories about the couple."""
    import random
    
    secrets = [
        "Did you know Moatasem once tried to surprise Hala with a picnic, but ended up getting lost in their own neighborhood for two hours? True love finds its way! 💕",
        "Hala's secret talent? She can recite every line from The Princess Bride perfectly, and Moatasem knows this is her ultimate weakness for romance! 📖✨",
        "Moatasem claims he's 'terrible at dancing,' but Hala caught him practicing wedding waltz moves in the living room when he thought she was asleep! 💃🕺",
        "Hala once told Moatasem that her dream wedding would have 'zero drama,' and Moatasem immediately started planning the most magical, drama-free celebration imaginable! 🎭✨",
        "Moatasem's hidden superpower? He can make Hala laugh even on her worst days with his perfectly timed dad jokes. The man is a comedy genius! 😂💍",
        "Hala secretly loves that Moatasem sings off-key in the shower every morning, calling it his 'personal alarm clock' that she wouldn't trade for anything! 🎵❤️",
        "Moatasem once surprised Hala with tickets to see her favorite band, but accidentally bought them for the wrong date - three months too early! Time flies when you're in love! 🎫💕",
        "Hala's guilty pleasure? Midnight ice cream runs with Moatasem, where they share ridiculous conspiracy theories about their favorite TV shows! 🍦🕵️‍♀️",
        "Moatasem claims he 'can't cook,' but Hala knows his secret: he's been perfecting his grandmother's famous baklava recipe just for their wedding dessert! 🧁👨‍🍳",
        "Hala once challenged Moatasem to a cooking competition, and he won by making 'love soup' - basically chicken noodle with extra heart! ❤️🍲"
    ]
    
    selected_secret = random.choice(secrets)
    print(f"[COUPLE SECRET] Sharing: {selected_secret}")
    
    # Display the secret on the mirror
    display_text = "A sweet secret about Moatasem & Hala! 💕"
    await update_display(display_text)
    
    return selected_secret

