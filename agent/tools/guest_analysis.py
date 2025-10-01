import asyncio
from typing import Dict, Any, Optional
from .base_tool import BaseTool


class GuestAnalysisTool(BaseTool):
    """Tool for analyzing guests and providing personalized interactions"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guest_data = {}  # Cache for guest information
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute guest analysis actions"""
        self._log_execution("GuestAnalysis", f"Action: {action}")
        
        if action == "analyze_voice":
            return await self._analyze_voice_command(kwargs.get("command", ""), kwargs.get("participant_id", ""))
        elif action == "get_guest_profile":
            return await self._get_guest_profile(kwargs.get("participant_id", ""))
        elif action == "update_guest_info":
            return await self._update_guest_info(kwargs.get("participant_id", ""), kwargs.get("info", {}))
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    async def _analyze_voice_command(self, command: str, participant_id: str) -> Dict[str, Any]:
        """Analyze voice command from a guest"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        command_lower = command.lower()
        analysis = {
            "participant_id": participant_id,
            "command": command,
            "intent": self._extract_intent(command_lower),
            "sentiment": self._analyze_sentiment(command_lower),
            "response_type": "default"
        }
        
        # Update guest interaction history
        if participant_id not in self.guest_data:
            self.guest_data[participant_id] = {"interactions": [], "preferences": {}}
        
        self.guest_data[participant_id]["interactions"].append({
            "command": command,
            "intent": analysis["intent"],
            "timestamp": asyncio.get_event_loop().time()
        })
        
        return {
            "success": True,
            "analysis": analysis,
            "response": f"Voice command analyzed for guest {participant_id}"
        }
    
    def _extract_intent(self, command: str) -> str:
        """Extract intent from voice command"""
        if "mirror mirror" in command:
            return "activate_mirror"
        elif any(word in command for word in ["compliment", "beautiful", "pretty", "gorgeous"]):
            return "request_compliment"
        elif any(word in command for word in ["celebration", "party", "dance", "music"]):
            return "celebration_mode"
        elif any(word in command for word in ["reset", "clear", "stop"]):
            return "reset_mirror"
        elif any(word in command for word in ["photo", "picture", "selfie"]):
            return "take_photo"
        else:
            return "general_interaction"
    
    def _analyze_sentiment(self, command: str) -> str:
        """Analyze sentiment of the command"""
        positive_words = ["beautiful", "amazing", "wonderful", "love", "happy", "joy", "celebration"]
        negative_words = ["sad", "angry", "upset", "bad", "terrible"]
        
        positive_count = sum(1 for word in positive_words if word in command)
        negative_count = sum(1 for word in negative_words if word in command)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    async def _get_guest_profile(self, participant_id: str) -> Dict[str, Any]:
        """Get stored profile information for a guest"""
        profile = self.guest_data.get(participant_id, {
            "interactions": [],
            "preferences": {},
            "first_seen": asyncio.get_event_loop().time()
        })
        
        return {
            "success": True,
            "participant_id": participant_id,
            "profile": profile,
            "response": f"Profile retrieved for guest {participant_id}"
        }
    
    async def _update_guest_info(self, participant_id: str, info: Dict[str, Any]) -> Dict[str, Any]:
        """Update guest information"""
        if participant_id not in self.guest_data:
            self.guest_data[participant_id] = {"interactions": [], "preferences": {}}
        
        self.guest_data[participant_id].update(info)
        
        return {
            "success": True,
            "participant_id": participant_id,
            "updated_info": info,
            "response": f"Guest information updated for {participant_id}"
        }