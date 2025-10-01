"""
LiveKit service for managing rooms and generating tokens
"""
import os
from typing import Optional
from datetime import timedelta
from livekit import api
from app.core.config import settings


class LiveKitService:
    def __init__(self):
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        self.url = settings.LIVEKIT_URL
        
        # Validate required settings
        if not all([self.api_key, self.api_secret, self.url]):
            raise ValueError(
                "Missing LiveKit configuration. Please set LIVEKIT_URL, "
                "LIVEKIT_API_KEY, and LIVEKIT_API_SECRET environment variables."
            )
    
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


# Global service instance
livekit_service = LiveKitService()
