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
from app.core.config import settings
from app.core.auth import verify_password, require_auth, check_auth
from app.core.livekit_service import livekit_service
from app.api.v1.api import api_router
import asyncio
import json
from typing import List

# Try to import LiveKit service, but make it optional
try:
    from app.core.livekit_service import livekit_service
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
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001",  # Alternative React dev port
        "http://127.0.0.1:3001",
        "https://raheva.com",     # Production domain
        "http://raheva.com"       # Production domain (HTTP redirect)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)# Store the current mirror text and original text
original_text = '<span class="line fancy">Welcome to</span><span class="line fancy">x & y</span><span class="line fancy">Wedding</span><span class="line script">Say Mirror Mirror to begin</span>'
current_text = original_text

# Store connected clients for SSE
connected_clients: List[asyncio.Queue] = []

class TextUpdate(BaseModel):
    text: str

class AudioPlayEvent(BaseModel):
    type: str = "audio_play"
    message: str = "Playing mirror sound effect"

# Mount static files (removed - not needed)
# app.mount("/static", StaticFiles(directory="../static"), name="static")

# Store connected SSE clients
connected_clients: List[asyncio.Queue] = []

# Store the current mirror text and original text
original_text = '<span class="line fancy">Welcome to</span><span class="line fancy">x & y</span><span class="line fancy">Wedding</span><span class="line script">Say Mirror Mirror to begin</span>'
current_text = original_text

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

# Auth API routes - returning JSON instead of HTML templates
@app.get("/")
def root():
    """API root endpoint - redirect to React app"""
    return {"message": "Wedding Mirror API", "frontend_url": "http://localhost:3000"}

# Login endpoint moved to /api/login in api_router

# Mirror display endpoint moved to /api/mirror in api_router

# Logout endpoint moved to /api/logout in api_router

# Mirror control endpoints
@app.post("/api/reset")
async def reset_mirror():
    """Reset mirror to default text and play audio"""
    global current_text
    current_text = original_text
    
    # Broadcast reset message to all connected clients
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
    
    # Broadcast update to all connected clients
    event_data = {
        "type": "text_update", 
        "text": current_text
    }
    
    # Send to all connected clients
    disconnected_clients = []
    for client_queue in connected_clients:
        try:
            await client_queue.put(event_data)
        except:
            disconnected_clients.append(client_queue)
    
    # Remove disconnected clients
    for client in disconnected_clients:
        connected_clients.remove(client)
    
    return {
        "message": "Text updated successfully", 
        "new_text": current_text,
        "clients_notified": len(connected_clients)
    }


