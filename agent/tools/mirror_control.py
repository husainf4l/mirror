from typing import Dict, Any
from .base_tool import BaseTool


class MirrorControlTool(BaseTool):
    """Tool for controlling the wedding mirror display and audio"""
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute mirror control actions"""
        self._log_execution("MirrorControl", f"Action: {action}")
        
        if action == "update_display":
            return await self._update_display(kwargs.get("message", ""))
        elif action == "reset":
            return await self._reset_mirror()
        elif action == "play_audio":
            return await self._play_audio()
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    async def _update_display(self, message: str) -> Dict[str, Any]:
        """Update the mirror display with a message"""
        success = await self._make_api_call("/update-text", {"text": message})
        return {
            "success": success,
            "action": "update_display",
            "message": message,
            "response": "Mirror display updated" if success else "Failed to update display"
        }
    
    async def _reset_mirror(self) -> Dict[str, Any]:
        """Reset mirror to default state"""
        success = await self._make_api_call("/reset")
        return {
            "success": success,
            "action": "reset",
            "response": "Mirror reset to default" if success else "Failed to reset mirror"
        }
    
    async def _play_audio(self) -> Dict[str, Any]:
        """Play mirror audio effect"""
        success = await self._make_api_call("/play-audio")
        return {
            "success": success,
            "action": "play_audio", 
            "response": "Audio played" if success else "Failed to play audio"
        }