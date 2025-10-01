from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from app.core.auth import verify_password, require_auth
from app.core.livekit_service import livekit_service
from app.core.config import settings
import asyncio
import json

api_router = APIRouter()

@api_router.get("/")
def api_root():
    """API root endpoint"""
    return {"message": "Wedding Mirror API", "version": "1.0.0"}

@api_router.post("/login")
def login(password: str = Form(...)):
    """Handle login form submission - returns JSON for React"""
    if verify_password(password):
        response = JSONResponse({
            "success": True,
            "message": "Login successful"
        })
        response.set_cookie(
            key="mirror_auth",
            value=password,  # Simple: store password as cookie
            max_age=86400,  # 24 hours
            httponly=True,
            secure=False  # Set to True if using HTTPS
        )
        return response
    else:
        return JSONResponse({
            "success": False,
            "error": "Invalid password. Please try again."
        }, status_code=401)

@api_router.post("/logout")
def logout():
    """Logout and clear auth cookie - returns JSON"""
    response = JSONResponse({"success": True, "message": "Logged out successfully"})
    response.delete_cookie(key="mirror_auth")
    return response

@api_router.get("/mirror")
def mirror_display(authenticated: bool = Depends(require_auth)):
    """API endpoint to get mirror state - requires authentication"""
    # Import here to avoid circular imports
    from app.main import current_text, original_text
    return {
        "success": True,
        "current_text": current_text,
        "original_text": original_text
    }

@api_router.post("/livekit/token")
async def get_livekit_token(request: Request):
    """Generate LiveKit access token for joining a room"""
    data = await request.json()
    
    room_name = data.get("room", "mirror-room")
    participant_name = data.get("name", "Anonymous")
    identity = data.get("identity", participant_name)
    
    try:
        connection_details = livekit_service.get_connection_details(
            room_name=room_name,
            participant_name=participant_name,
            identity=identity
        )
        
        return {
            "success": True,
            "token": connection_details["token"],
            "url": connection_details["url"],
            "room": room_name,
            "identity": identity
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@api_router.get("/livekit/config")
def get_livekit_config():
    """Get LiveKit configuration for frontend"""
    return {
        "url": settings.LIVEKIT_URL,
        "default_room": "mirror-room"
    }

@api_router.get("/events")
async def stream_events(request: Request):
    """Server-sent events for real-time mirror updates"""
    # Import here to avoid circular imports
    from app.main import connected_clients, current_text
    
    async def event_generator():
        client_queue = asyncio.Queue()
        connected_clients.append(client_queue)
        
        try:
            # Send initial connection confirmation
            initial_message = {
                "type": "connected", 
                "message": "Connected to mirror",
                "current_text": current_text
            }
            yield f"data: {json.dumps(initial_message)}\n\n"
            
            # Listen for messages
            while True:
                try:
                    # Wait for message with timeout to send periodic pings
                    message = await asyncio.wait_for(client_queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    ping_message = {"type": "ping", "timestamp": asyncio.get_event_loop().time()}
                    yield f"data: {json.dumps(ping_message)}\n\n"
                    
        except Exception as e:
            print(f"SSE client disconnected: {e}")
        finally:
            # Remove client from connected list
            if client_queue in connected_clients:
                connected_clients.remove(client_queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
        }
    )
