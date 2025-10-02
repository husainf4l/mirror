"""
Agent Functions for Wedding Mirror

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
            if __main__.current_agent.recording_manager:
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
            f'<span class="line fancy">To Rakan & Farah</span>'
            f'<span class="line script">Enjoy the celebration!</span>'
        )
        display_message = f"Welcome {clean_name}! To Rakan & Farah - Enjoy the celebration!"
    else:
        # Format as general message for compliments or other text
        formatted_text = (
            f'<span class="line fancy">{display_text}</span>'
            f'<span class="line fancy">To Rakan & Farah</span>'
            f'<span class="line script">Enjoy the celebration!</span>'
        )
        display_message = f"{display_text} - To Rakan & Farah - Enjoy the celebration!"

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
    """Start a new mirror session when activated with 'mirror mirror' - plays activation audio and starts recording for the guest."""
    print("[AUDIO] Playing mirror activation sound - Starting new guest recording")
    
    # Start recording when mirror is activated
    try:
        import __main__
        if hasattr(__main__, 'current_agent') and __main__.current_agent:
            agent = __main__.current_agent
            
            # Initialize fresh recording manager for this guest
            print("[RECORDING] Initializing new RecordingManager for guest...")
            from utils.recording import RecordingManager
            agent.recording_manager = RecordingManager(agent.ctx)
            print("[RECORDING] New RecordingManager initialized successfully")
            
            # Start recording
            if agent.recording_manager:
                print("[RECORDING] Starting recording...")
                recording_url = await agent.recording_manager.start_recording()
                if recording_url:
                    print(f"[RECORDING] Recording started successfully and saved to backend: {recording_url}")
                else:
                    print("[RECORDING] LiveKit recording failed (likely egress minutes exceeded), but continuing with session")
                    print("[RECORDING] Guest can still use mirror - video recording unavailable")
                    # Clear the recording manager since recording failed
                    agent.recording_manager = None
            else:
                print("[RECORDING] No recording manager available")
        else:
            print("[RECORDING] No agent instance available for recording")
    except Exception as e:
        print(f"[RECORDING] Error starting recording: {e}")
        import logging
        logging.error(f"Error starting recording in start_session: {e}", exc_info=True)
    
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
async def reset_for_next_guest() -> str:
    """Reset the mirror display for the next guest while keeping the recording active."""
    print("[AGENT ACTION] Resetting mirror for next guest - keeping recording active")
    
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
                    return "Mirror reset successfully. Ready for next guest activation with 'mirror mirror'. Recording continues in background."
                else:
                    return f"Mirror reset failed (status: {response.status}). Ready for next activation."
    except subprocess.CalledProcessError as e:
        return f"Failed to play closing audio: {e}. Mirror reset for next guest."
    except aiohttp.ClientError as e:
        return f"Failed to reset mirror: {e}. Ready for next guest."
    except Exception as e:
        return f"Error resetting for next guest: {e}"


@function_tool
async def close_session() -> str:
    """Close current guest session, stop their recording, reset mirror, and prepare for next guest."""
    print("[AGENT ACTION] Closing guest session - stopping recording and resetting mirror")
    
    # Stop current guest's recording
    recording_stopped = False
    
    try:
        import __main__
        if hasattr(__main__, 'current_agent') and __main__.current_agent:
            agent = __main__.current_agent
            
            if hasattr(agent, 'recording_manager') and agent.recording_manager:
                print("[RECORDING] Stopping current guest's recording...")
                
                # Stop the recording for this guest
                success = await agent.recording_manager.stop_recording()
                if success:
                    print("[RECORDING] Guest recording stopped and saved successfully")
                    recording_stopped = True
                else:
                    print("[RECORDING] Failed to stop guest recording (may not have been started)")
                
                # Clear the recording manager so next guest gets a fresh one
                agent.recording_manager = None
                print("[RECORDING] Cleared recording manager for next guest")
            else:
                print("[RECORDING] No active recording to stop - recording may have failed to start")
        else:
            print("[RECORDING] No agent instance available")
    except Exception as e:
        print(f"[RECORDING] Error during guest recording cleanup: {e}")
        import logging
        logging.error(f"Error stopping recording in close_session: {e}", exc_info=True)
    
    # Reset the mirror via backend API
    import aiohttp
    try:
        url = "http://localhost:8000/api/reset"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    print("[MIRROR DISPLAY] Mirror reset to default state - ready for next guest")
                    
                    if recording_stopped:
                        return "✨ *Magical Farewell Chime* 🔮 Farewell, beautiful soul! Until we meet again! *The mirror sleeps...*"
                    else:
                        return "✨ *Magical Farewell Chime* 🔮 Farewell, beautiful soul! Until we meet again! *The mirror sleeps...*"
                else:
                    return f"✨ *Magical Farewell Chime* 🔮 Farewell! *The mirror sleeps...* (Mirror reset had issues: {response.status})"
    except Exception as e:
        return f"✨ *Magical Farewell Chime* 🔮 Farewell, beautiful soul! Until we meet again! *The mirror sleeps...* (Reset error: {e})"


@function_tool
async def stop_recording_session() -> str:
    """Stop the recording session completely when all guests are done."""
    print("[AGENT ACTION] Stopping recording session completely")
    
    # Stop recording and mark as completed
    recording_stopped = False
    
    try:
        import __main__
        if hasattr(__main__, 'current_agent') and __main__.current_agent:
            agent = __main__.current_agent
            
            if hasattr(agent, 'recording_manager') and agent.recording_manager:
                print("[RECORDING] Stopping recording session...")
                
                # Stop the recording
                success = await agent.recording_manager.stop_recording()
                if success:
                    print("[RECORDING] Recording stopped and marked as completed in backend")
                    recording_stopped = True
                else:
                    print("[RECORDING] Failed to stop recording")
            else:
                print("[RECORDING] No recording manager available to stop")
        else:
            print("[RECORDING] No agent instance available for recording cleanup")
    except Exception as e:
        print(f"[RECORDING] Error during recording cleanup: {e}")
        import logging
        logging.error(f"Error stopping recording: {e}", exc_info=True)
    
    if recording_stopped:
        return "Recording session stopped successfully. All guest interactions have been saved to the backend."
    else:
        return "Failed to stop recording session or no recording was active."


