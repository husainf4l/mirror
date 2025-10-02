"""
Mirror Text Update Tool

This tool allows the agent to update the mirror text display by calling the FastAPI endpoint.
"""

import asyncio
import aiohttp
import json
from typing import Optional


class MirrorTextTool:
    """Tool for updating mirror text display via FastAPI endpoint"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the mirror text tool
        
        Args:
            base_url: Base URL of the FastAPI backend
        """
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/api/update-text"
    
    async def update_text(self, text: str) -> dict:
        """
        Update the mirror text display
        
        Args:
            text: The new text to display on the mirror (supports HTML formatting)
            
        Returns:
            dict: Response from the API with success status and client count
        """
        payload = {
            "text": text
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "message": result.get("message", "Text updated successfully"),
                            "new_text": result.get("new_text", text),
                            "clients_notified": result.get("clients_notified", 0)
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {await response.text()}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }
    
    async def update_wedding_text(self, bride_name: str, groom_name: str, message: str = "Say Mirror Mirror to begin") -> dict:
        """
        Update mirror with wedding-specific text formatting
        
        Args:
            bride_name: Name of the bride
            groom_name: Name of the groom  
            message: Custom message (default: "Say Mirror Mirror to begin")
            
        Returns:
            dict: Response from the API
        """
        formatted_text = (
            f'<span class="line fancy">Welcome to</span>'
            f'<span class="line fancy">{groom_name} & {bride_name}</span>'
            f'<span class="line fancy">Wedding</span>'
            f'<span class="line script">{message}</span>'
        )
        
        return await self.update_text(formatted_text)
    
    async def update_custom_message(self, lines: list) -> dict:
        """
        Update mirror with custom multi-line message
        
        Args:
            lines: List of text lines to display
            
        Returns:
            dict: Response from the API
        """
        formatted_text = ""
        for i, line in enumerate(lines):
            css_class = "fancy" if i < len(lines) - 1 else "script"
            formatted_text += f'<span class="line {css_class}">{line}</span>'
        
        return await self.update_text(formatted_text)


# Example usage functions for the agent
async def update_mirror_text(text: str, base_url: str = "http://localhost:8000") -> dict:
    """
    Convenient function to update mirror text
    
    Args:
        text: Text to display on mirror
        base_url: Backend API base URL
        
    Returns:
        dict: Update result
    """
    tool = MirrorTextTool(base_url)
    return await tool.update_text(text)


async def update_wedding_mirror(bride: str, groom: str, base_url: str = "http://localhost:8000") -> dict:
    """
    Convenient function to update mirror with wedding names
    
    Args:
        bride: Bride's name
        groom: Groom's name
        base_url: Backend API base URL
        
    Returns:
        dict: Update result
    """
    tool = MirrorTextTool(base_url)
    return await tool.update_wedding_text(bride, groom)


# Tool metadata for agent integration
TOOL_INFO = {
    "name": "mirror_text_tool",
    "description": "Update the wedding mirror text display via FastAPI endpoint",
    "functions": [
        {
            "name": "update_text",
            "description": "Update mirror with raw HTML text",
            "parameters": {
                "text": "HTML formatted text to display"
            }
        },
        {
            "name": "update_wedding_text", 
            "description": "Update mirror with wedding names",
            "parameters": {
                "bride_name": "Name of the bride",
                "groom_name": "Name of the groom",
                "message": "Optional custom message"
            }
        },
        {
            "name": "update_custom_message",
            "description": "Update mirror with custom multi-line message", 
            "parameters": {
                "lines": "List of text lines to display"
            }
        }
    ]
}


if __name__ == "__main__":
    # Test the tool
    async def test_tool():
        tool = MirrorTextTool()
        
        # Test basic text update
        result = await tool.update_text("Hello from the agent!")
        print("Basic update:", result)
        
        # Test wedding text update
        result = await tool.update_wedding_text("y", "x")
        print("Wedding update:", result)
        
        # Test custom message
        result = await tool.update_custom_message([
            "Welcome Everyone!",
            "To our special day",
            "Please take a seat"
        ])
        print("Custom message:", result)
    
    # Run test
    asyncio.run(test_tool())