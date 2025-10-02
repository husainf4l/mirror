"""
Agent Functions for Wedding Mirror

This module contains all the function tools used by the wedding mirror agent.
"""

import asyncio
import aiohttp
import subprocess
from livekit.agents.llm import function_tool


@function_tool
async def get_guest_about(guest_name: str) -> str:
    """Get detailed information about a guest from their 'about' field in the wedding database."""
    print(f"[DEBUG] get_guest_about called with guest_name: '{guest_name}'")

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
                            about_info = guest_info.get("about", "")

                            if about_info and about_info.strip():
                                print(f"[DEBUG] Successfully found about info for: {full_name}")
                                return f"About {full_name}: {about_info}"
                            else:
                                print(f"[DEBUG] No about info found for: {full_name}")
                                return f"I don't have any additional information about {full_name} in our records."

        except aiohttp.ClientError as e:
            print(f"[DEBUG] Client error for '{variation}': {e}")
            continue
        except Exception as e:
            print(f"[DEBUG] Exception for '{variation}': {str(e)}")
            continue

    # If no variations worked, return not found message
    print(f"[DEBUG] No guest found for any variation of '{guest_name}'")
    return f"I couldn't find any information about '{guest_name}' in our wedding records."


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
    clean_name = correct_name.title()
    
    formatted_text = (
        f'<span class="line fancy">Welcome</span>'
        f'<span class="line fancy">{clean_name}!</span>'
        f'<span class="line fancy">To X & Y</span>'
        f'<span class="line script">Enjoy the celebration!</span>'
    )
    
    print(f"[MIRROR DISPLAY] Updating mirror text to: Welcome {clean_name}! To X & Y - Enjoy the celebration!")
    
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
    clean_name = guest_name.title()
    
    formatted_text = (
        f'<span class="line fancy">Welcome</span>'
        f'<span class="line fancy">{clean_name}!</span>'
        f'<span class="line fancy">To X & Y</span>'
        f'<span class="line script">Enjoy the celebration!</span>'
    )
    
    print(f"[MIRROR DISPLAY] Updating mirror text to: Welcome {clean_name}! To X & Y - Enjoy the celebration!")
    
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
@function_tool
async def play_mirror_audio() -> str:
    """Play the mirror activation audio when activated with 'mirror mirror'."""
    print("[AUDIO] Playing mirror activation sound")
    
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
    
    import subprocess
    try:
        # Play the mirror.wav file
        subprocess.run(['aplay', '/home/husain/Desktop/mirror/agent/mirror.wav'], check=True)
        return "Mirror activated with magical sound!"
    except subprocess.CalledProcessError as e:
        return f"Failed to play mirror audio: {e}"
    except FileNotFoundError:
        return "Audio player 'aplay' not found. Please install alsa-utils."


@function_tool
async def close_session() -> str:
    """Close the current session, play closing audio, and reset the mirror when the guest finishes or stops responding."""
    print("[AGENT ACTION] Closing session - playing closing audio and resetting mirror")
    import subprocess
    import aiohttp
    try:
        # Play the closing.wav file
        subprocess.run(['aplay', '/home/husain/Desktop/mirror/agent/closing.wav'], check=True)
        
        # Reset the mirror via backend API
        url = "http://localhost:8000/api/reset"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    print("[MIRROR DISPLAY] Mirror reset to default state")
                    return "Session closed successfully. Mirror reset and ready for next activation with 'mirror mirror'."
                else:
                    return f"Session closed but mirror reset failed (status: {response.status}). Ready for next activation."
    except subprocess.CalledProcessError as e:
        return f"Failed to play closing audio: {e}. Session closed and mirror reset."
    except aiohttp.ClientError as e:
        return f"Failed to reset mirror: {e}. Session closed."
    except Exception as e:
        return f"Error closing session: {e}"