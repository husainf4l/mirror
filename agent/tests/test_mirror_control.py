import pytest
import asyncio
from unittest.mock import patch, AsyncMock
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.mirror_control import MirrorControlTool


class TestMirrorControlTool:
    """Test suite for MirrorControlTool"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tool = MirrorControlTool()
    
    @pytest.mark.asyncio
    async def test_update_display_success(self):
        """Test successful display update"""
        with patch.object(self.tool, '_make_api_call', return_value=True):
            result = await self.tool.execute("update_display", message="Test message")
            
            assert result["success"] is True
            assert result["action"] == "update_display"
            assert result["message"] == "Test message"
            assert "updated" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_update_display_failure(self):
        """Test failed display update"""
        with patch.object(self.tool, '_make_api_call', return_value=False):
            result = await self.tool.execute("update_display", message="Test message")
            
            assert result["success"] is False
            assert "failed" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_reset_mirror_success(self):
        """Test successful mirror reset"""
        with patch.object(self.tool, '_make_api_call', return_value=True):
            result = await self.tool.execute("reset")
            
            assert result["success"] is True
            assert result["action"] == "reset"
            assert "reset" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_reset_mirror_failure(self):
        """Test failed mirror reset"""
        with patch.object(self.tool, '_make_api_call', return_value=False):
            result = await self.tool.execute("reset")
            
            assert result["success"] is False
            assert "failed" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_play_audio_success(self):
        """Test successful audio playback"""
        with patch.object(self.tool, '_make_api_call', return_value=True):
            result = await self.tool.execute("play_audio")
            
            assert result["success"] is True
            assert result["action"] == "play_audio"
            assert "played" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_play_audio_failure(self):
        """Test failed audio playback"""
        with patch.object(self.tool, '_make_api_call', return_value=False):
            result = await self.tool.execute("play_audio")
            
            assert result["success"] is False
            assert "failed" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_unknown_action(self):
        """Test unknown action handling"""
        result = await self.tool.execute("unknown_action")
        
        assert result["success"] is False
        assert "unknown action" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_api_calls_made_correctly(self):
        """Test that correct API calls are made"""
        with patch.object(self.tool, '_make_api_call', return_value=True) as mock_api:
            
            # Test update display
            await self.tool.execute("update_display", message="Test")
            mock_api.assert_called_with("/update-text", {"text": "Test"})
            
            # Test reset
            await self.tool.execute("reset")
            mock_api.assert_called_with("/reset")
            
            # Test play audio
            await self.tool.execute("play_audio")
            mock_api.assert_called_with("/play-audio")


if __name__ == "__main__":
    pytest.main([__file__])