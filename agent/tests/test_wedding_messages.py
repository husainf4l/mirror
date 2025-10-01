import pytest
import asyncio
from unittest.mock import patch
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.wedding_messages import WeddingMessagesTool


class TestWeddingMessagesTool:
    """Test suite for WeddingMessagesTool"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tool = WeddingMessagesTool()
    
    @pytest.mark.asyncio
    async def test_celebration_message(self):
        """Test celebration message generation"""
        result = await self.tool.execute("celebration")
        
        assert result["success"] is True
        assert result["type"] == "celebration"
        assert "message" in result
        assert result["message"] in self.tool.celebration_messages
        assert "celebration message generated" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_romantic_message(self):
        """Test romantic message generation"""
        result = await self.tool.execute("romantic")
        
        assert result["success"] is True
        assert result["type"] == "romantic"
        assert "message" in result
        assert result["message"] in self.tool.romantic_messages
        assert "romantic message generated" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_welcome_message(self):
        """Test welcome message generation"""
        result = await self.tool.execute("welcome")
        
        assert result["success"] is True
        assert result["type"] == "welcome"
        assert "Ibrahim & Zaina" in result["message"]
        assert "welcome message generated" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_custom_message_with_text(self):
        """Test custom message creation with text"""
        custom_text = "Happy Wedding Day"
        result = await self.tool.execute("custom", text=custom_text)
        
        assert result["success"] is True
        assert result["type"] == "custom"
        assert custom_text in result["message"]
        assert 'class="line fancy"' in result["message"]
        assert "custom message created" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_custom_message_without_text(self):
        """Test custom message creation without text"""
        result = await self.tool.execute("custom")
        
        assert result["success"] is False
        assert "no text provided" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_unknown_message_type(self):
        """Test unknown message type handling"""
        result = await self.tool.execute("unknown_type")
        
        assert result["success"] is False
        assert "unknown message type" in result["error"].lower()
    
    def test_message_lists_not_empty(self):
        """Test that message lists are properly initialized"""
        assert len(self.tool.celebration_messages) > 0
        assert len(self.tool.romantic_messages) > 0
        
        # Check that all messages contain proper HTML formatting
        for message in self.tool.celebration_messages:
            assert 'span class="line' in message
        
        for message in self.tool.romantic_messages:
            assert 'span class="line' in message
    
    @pytest.mark.asyncio
    async def test_message_randomness(self):
        """Test that messages are randomized"""
        # Run multiple times to check for randomness
        messages = []
        for _ in range(10):
            result = await self.tool.execute("celebration")
            messages.append(result["message"])
        
        # Should have some variety (not all the same message)
        unique_messages = set(messages)
        assert len(unique_messages) > 1 or len(self.tool.celebration_messages) == 1


if __name__ == "__main__":
    pytest.main([__file__])