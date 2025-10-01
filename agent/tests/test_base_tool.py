import pytest
import asyncio
import logging
from unittest.mock import patch, AsyncMock
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.base_tool import BaseTool


class TestTool(BaseTool):
    """Test implementation of BaseTool"""
    
    async def execute(self, action="test", **kwargs):
        return {"success": True, "action": action, "kwargs": kwargs}


class TestBaseTool:
    """Test suite for BaseTool class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tool = TestTool()
    
    def test_init(self):
        """Test tool initialization"""
        assert self.tool.mirror_api_base == "http://localhost:8000/api"
        assert self.tool.logger.name == "wedding-mirror-tools.TestTool"
    
    def test_init_custom_api_base(self):
        """Test tool initialization with custom API base"""
        custom_tool = TestTool("http://example.com/api")
        assert custom_tool.mirror_api_base == "http://example.com/api"
    
    @pytest.mark.asyncio
    async def test_execute(self):
        """Test abstract execute method implementation"""
        result = await self.tool.execute("test_action", param1="value1")
        assert result["success"] is True
        assert result["action"] == "test_action"
        assert result["kwargs"]["param1"] == "value1"
    
    @pytest.mark.asyncio
    async def test_make_api_call_success(self):
        """Test successful API call"""
        result = await self.tool._make_api_call("/test", {"data": "test"})
        assert result is True
    
    @pytest.mark.asyncio
    async def test_make_api_call_with_exception(self):
        """Test API call with exception handling"""
        with patch('asyncio.sleep', side_effect=Exception("Network error")):
            result = await self.tool._make_api_call("/test")
            assert result is False
    
    def test_log_execution(self):
        """Test logging functionality"""
        with patch.object(self.tool.logger, 'info') as mock_logger:
            self.tool._log_execution("test_action", "test details")
            mock_logger.assert_called_once_with("test_action: test details")


if __name__ == "__main__":
    pytest.main([__file__])