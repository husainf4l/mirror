import random
from typing import Dict, Any, List
from .base_tool import BaseTool


class WeddingMessagesTool(BaseTool):
    """Tool for generating and managing wedding messages"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.celebration_messages = [
            '<span class="line fancy">Welcome to</span><span class="line fancy">Ibrahim & Zaina</span><span class="line fancy">Wedding</span>',
            '<span class="line fancy">Let the</span><span class="line script">Celebration</span><span class="line fancy">Begin!</span>',
            '<span class="line script">May your love</span><span class="line fancy">Shine Forever</span><span class="line script">together</span>',
            '<span class="line fancy">Blessed Union</span><span class="line script">of</span><span class="line fancy">Two Hearts</span>',
            '<span class="line script">Wishing you</span><span class="line fancy">Eternal Joy</span><span class="line script">& Happiness</span>'
        ]
        
        self.romantic_messages = [
            '<span class="line script">Love is in</span><span class="line fancy">The Air</span><span class="line script">tonight</span>',
            '<span class="line fancy">Two Hearts</span><span class="line script">beating as</span><span class="line fancy">One</span>',
            '<span class="line script">Forever</span><span class="line fancy">& Always</span><span class="line script">together</span>',
            '<span class="line fancy">Perfect</span><span class="line script">love story</span><span class="line fancy">Continues</span>',
            '<span class="line script">Sealed with</span><span class="line fancy">True Love</span><span class="line script">& Joy</span>'
        ]
    
    async def execute(self, message_type: str, **kwargs) -> Dict[str, Any]:
        """Generate wedding messages based on type"""
        self._log_execution("WeddingMessages", f"Type: {message_type}")
        
        if message_type == "celebration":
            return await self._get_celebration_message()
        elif message_type == "romantic":
            return await self._get_romantic_message()
        elif message_type == "custom":
            return await self._create_custom_message(kwargs.get("text", ""))
        elif message_type == "welcome":
            return await self._get_welcome_message()
        else:
            return {"success": False, "error": f"Unknown message type: {message_type}"}
    
    async def _get_celebration_message(self) -> Dict[str, Any]:
        """Get a random celebration message"""
        message = random.choice(self.celebration_messages)
        return {
            "success": True,
            "type": "celebration",
            "message": message,
            "response": "Celebration message generated"
        }
    
    async def _get_romantic_message(self) -> Dict[str, Any]:
        """Get a random romantic message"""
        message = random.choice(self.romantic_messages)
        return {
            "success": True,
            "type": "romantic",
            "message": message,
            "response": "Romantic message generated"
        }
    
    async def _create_custom_message(self, text: str) -> Dict[str, Any]:
        """Create a custom formatted message"""
        if not text:
            return {"success": False, "error": "No text provided for custom message"}
        
        formatted_message = f'<span class="line fancy">{text}</span>'
        return {
            "success": True,
            "type": "custom",
            "message": formatted_message,
            "response": "Custom message created"
        }
    
    async def _get_welcome_message(self) -> Dict[str, Any]:
        """Get the default welcome message"""
        message = '<span class="line fancy">Welcome to</span><span class="line fancy">Ibrahim & Zaina</span><span class="line fancy">Wedding</span>'
        return {
            "success": True,
            "type": "welcome",
            "message": message,
            "response": "Welcome message generated"
        }