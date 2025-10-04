import os
from dotenv import load_dotenv

# Load environment variables from parent directory FIRST
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from fastapi import FastAPI, Request, Form, Cookie, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import json
from typing import List
from backend.app.core.config import settings
from backend.app.core.auth import verify_password, require_auth, check_auth
from backend.app.api.v1.api import api_router

# Try to import LiveKit service, but make it optional
try:
    from backend.app.core.livekit_service import livekit_service
    LIVEKIT_AVAILABLE = True
except ValueError as e:
    print(f"Warning: LiveKit service not available: {e}")
    livekit_service = None
    LIVEKIT_AVAILABLE = False

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Add CORS middleware to allow React app to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store the current mirror text and original text
original_text = '<span class="line welcome fancy">Welcome to</span><span class="line names fancy">Moatasem & Hala Wedding</span><span class="line script">Say Mirror Mirror to begin</span>'
current_text = original_text

# Store connected clients for SSE
connected_clients: List[asyncio.Queue] = []

class TextUpdate(BaseModel):
    text: str

class AudioPlayEvent(BaseModel):
    type: str = "audio_play"
    message: str = "Playing mirror sound effect"

async def broadcast_message(message: dict):
    """Broadcast message to all connected SSE clients"""
    if connected_clients:
        disconnected_clients = []
        for client_queue in connected_clients:
            try:
                await client_queue.put(message)
            except Exception:
                disconnected_clients.append(client_queue)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            connected_clients.remove(client)

# Include API routes
app.include_router(api_router, prefix="/api")

# Auth API routes
@app.get("/")
def root():
    """API root endpoint"""
    return {"message": "Wedding Mirror API", "frontend_url": "http://localhost:3000"}

# Mirror control endpoints
@app.post("/api/reset")
async def reset_mirror():
    """Reset mirror to default text and play audio"""
    global current_text
    current_text = original_text
    
    reset_message = {
        "type": "reset",
        "new_text": current_text,
        "play_audio": True,
        "message": "Mirror reset to default"
    }
    
    await broadcast_message(reset_message)
    
    return {
        "success": True,
        "message": "Mirror reset to default",
        "new_text": current_text,
        "play_audio": True,
        "audio_url": "/static/audio/mirror.wav"
    }

@app.post("/api/update-text")
async def update_text(text_update: TextUpdate):
    """Update the mirror text display"""
    global current_text, connected_clients
    
    current_text = text_update.text
    
    event_data = {
        "type": "text_update", 
        "text": current_text
    }
    
    disconnected_clients = []
    for client_queue in connected_clients:
        try:
            await client_queue.put(event_data)
        except:
            disconnected_clients.append(client_queue)
    
    for client in disconnected_clients:
        connected_clients.remove(client)
    
    return {
        "message": "Text updated successfully", 
        "new_text": current_text,
        "clients_notified": len(connected_clients)
    }

@app.post("/api/play-audio")
async def play_audio(request: dict):
    """Trigger audio playback in the frontend"""
    audio_file = request.get("audio_file", "mirror_activation.wav")
    action = request.get("action", "play_sound")
    
    # Create audio play event
    audio_event = {
        "type": "audio_play",
        "audio_file": audio_file,
        "action": action,
        "message": "Playing mirror activation sound"
    }
    
    # Broadcast to all connected clients
    await broadcast_message(audio_event)
    
    return {
        "success": True,
        "message": f"Audio play command sent: {audio_file}",
        "clients_notified": len(connected_clients),
        "audio_file": audio_file,
        "action": action
    }
