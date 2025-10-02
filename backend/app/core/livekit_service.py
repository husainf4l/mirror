"""
LiveKit service for managing rooms and generating tokens
"""
import os
from typing import Optional, List, Dict, Any
from datetime import timedelta
import time
import jwt
import requests
import logging
from livekit import api
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class LiveKitService:
    """
    Service for managing LiveKit rooms and generating access tokens.
    
    This service provides methods to:
    - Generate access tokens for participants
    - List active rooms
    - Delete rooms
    - Get connection details for frontend clients
    """
    
    def __init__(self):
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        self.url = settings.LIVEKIT_URL
        self.api_base_url = self._get_api_base_url()
        
        # Validate required settings
        if not all([self.api_key, self.api_secret, self.url]):
            raise ValueError(
                "Missing LiveKit configuration. Please set LIVEKIT_URL, "
                "LIVEKIT_API_KEY, and LIVEKIT_API_SECRET environment variables."
            )
            
        logger.info("LiveKit service initialized successfully")
    
    def _get_api_base_url(self) -> str:
        """Extract API base URL from WebSocket URL"""
        if self.url.startswith('wss://'):
            # Convert wss://domain to https://domain for API calls
            return self.url.replace('wss://', 'https://')
        elif self.url.startswith('ws://'):
            # Convert ws://domain to http://domain for API calls
            return self.url.replace('ws://', 'http://')
        else:
            # Assume it's already an HTTP URL
            return self.url
    
    def generate_access_token(
        self, 
        room_name: str, 
        participant_name: str,
        identity: str,
        metadata: str = "",
        can_publish: bool = True,
        can_subscribe: bool = True,
        can_publish_data: bool = True,
        ttl_minutes: int = 60
    ) -> str:
        """
        Generate an access token for a participant to join a room
        """
        token = api.AccessToken(self.api_key, self.api_secret)
        token = token.with_identity(identity)
        token = token.with_name(participant_name)
        
        if metadata:
            token = token.with_metadata(metadata)
        
        # Set video grants
        grants = api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=can_publish,
            can_subscribe=can_subscribe,
            can_publish_data=can_publish_data
        )
        
        token = token.with_grants(grants)
        
        # Set TTL (convert minutes to seconds)
        ttl_seconds = ttl_minutes * 60
        token = token.with_ttl(timedelta(seconds=ttl_seconds))
        
        return token.to_jwt()
    
    def get_connection_details(self, room_name: str, participant_name: str, identity: str) -> dict:
        """
        Get connection details including token for joining a room
        """
        token = self.generate_access_token(room_name, participant_name, identity)
        
        return {
            "url": self.url,
            "token": token,
            "room_name": room_name,
            "participant_name": participant_name,
            "identity": identity
        }
    
    def _generate_admin_token(self, ttl_seconds: int = 300) -> str:
        """
        Generate admin JWT token for LiveKit API authentication.
        
        Args:
            ttl_seconds: Token time-to-live in seconds (default: 5 minutes)
            
        Returns:
            JWT token string
        """
        current_time = int(time.time())
        payload = {
            "iss": self.api_key,
            "sub": self.api_key,
            "iat": current_time,
            "exp": current_time + ttl_seconds,
            "video": {
                "room": "*",
                "roomList": True,
                "roomCreate": True,
                "roomJoin": False,
                "roomAdmin": True,
                "canPublish": False,
                "canSubscribe": False
            }
        }
        
        try:
            return jwt.encode(payload, self.api_secret, algorithm="HS256")
        except Exception as e:
            logger.error(f"Failed to generate admin token: {e}")
            raise
    
    def _make_api_request(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make authenticated request to LiveKit API.
        
        Args:
            endpoint: API endpoint (e.g., 'twirp/livekit.RoomService/ListRooms')
            data: Request payload
            
        Returns:
            JSON response data
            
        Raises:
            requests.RequestException: If API request fails
        """
        token = self._generate_admin_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making API request to: {url}")
            response = requests.post(url, headers=headers, json=data or {}, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"LiveKit API request failed: {e}")
            raise
    
    def list_rooms(self) -> List[str]:
        """
        List all active rooms.
        
        Returns:
            List of room names
            
        Raises:
            requests.RequestException: If API request fails
        """
        try:
            data = self._make_api_request("twirp/livekit.RoomService/ListRooms")
            rooms = data.get("rooms", [])
            room_names = [room.get("name", "") for room in rooms if room.get("name")]
            logger.info(f"Found {len(room_names)} active rooms")
            return room_names
        except Exception as e:
            logger.error(f"Failed to list rooms: {e}")
            return []
    
    def delete_room(self, room_name: str) -> bool:
        """
        Delete a specific room.
        
        Args:
            room_name: Name of the room to delete
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If room_name is empty
            requests.RequestException: If API request fails
        """
        if not room_name or not room_name.strip():
            raise ValueError("Room name cannot be empty")
            
        try:
            self._make_api_request("twirp/livekit.RoomService/DeleteRoom", {"room": room_name})
            logger.info(f"Successfully deleted room: {room_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete room '{room_name}': {e}")
            return False
    
    def delete_all_rooms(self) -> Dict[str, Any]:
        """
        Delete all active rooms.
        
        Returns:
            Dictionary with deletion results
        """
        try:
            rooms = self.list_rooms()
            if not rooms:
                return {"success": True, "deleted_count": 0, "message": "No rooms to delete"}
            
            deleted_count = 0
            failed_rooms = []
            
            for room_name in rooms:
                if self.delete_room(room_name):
                    deleted_count += 1
                else:
                    failed_rooms.append(room_name)
            
            result = {
                "success": len(failed_rooms) == 0,
                "deleted_count": deleted_count,
                "total_rooms": len(rooms),
                "failed_rooms": failed_rooms
            }
            
            if failed_rooms:
                result["message"] = f"Deleted {deleted_count}/{len(rooms)} rooms. Failed: {failed_rooms}"
            else:
                result["message"] = f"Successfully deleted all {deleted_count} rooms"
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete all rooms: {e}")
            return {
                "success": False,
                "deleted_count": 0,
                "error": str(e)
            }


# Global service instance
livekit_service = LiveKitService()
