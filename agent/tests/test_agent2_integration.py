import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAgent2Integration:
    """Integration tests for the refactored agent2.py"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Mock the livekit dependencies since they're not available in test environment
        self.mock_agent = MagicMock()
        self.mock_session = MagicMock()
        self.mock_context = MagicMock()
    
    @pytest.mark.asyncio
    async def test_tools_initialization(self):
        """Test that all tools are properly initialized"""
        # Import here to avoid import errors during setup
        with patch('agent2.google'), \
             patch('agent2.get_job_context'), \
             patch('agent2.Agent.__init__'):
            
            from agent2 import WeddingMirrorAssistant
            
            agent = WeddingMirrorAssistant()
            
            # Check that all tools are initialized
            assert hasattr(agent, 'mirror_control')
            assert hasattr(agent, 'wedding_messages')
            assert hasattr(agent, 'guest_analysis')
            assert hasattr(agent, 'image_compliments')
            
            # Check tool types
            from tools.mirror_control import MirrorControlTool
            from tools.wedding_messages import WeddingMessagesTool
            from tools.guest_analysis import GuestAnalysisTool
            from tools.image_compliments import ImageComplimentsTool
            
            assert isinstance(agent.mirror_control, MirrorControlTool)
            assert isinstance(agent.wedding_messages, WeddingMessagesTool)
            assert isinstance(agent.guest_analysis, GuestAnalysisTool)
            assert isinstance(agent.image_compliments, ImageComplimentsTool)
    
    @pytest.mark.asyncio
    async def test_process_mirror_command_mirror_activation(self):
        """Test mirror activation command processing"""
        with patch('agent2.google'), \
             patch('agent2.get_job_context'), \
             patch('agent2.Agent.__init__'):
            
            from agent2 import WeddingMirrorAssistant
            
            agent = WeddingMirrorAssistant()
            
            # Mock tool responses
            agent.wedding_messages.execute = AsyncMock(return_value={
                "success": True,
                "message": "Welcome message"
            })
            agent.mirror_control.execute = AsyncMock(return_value={
                "success": True,
                "response": "Mirror updated"
            })
            
            # Test mirror activation
            analysis_result = {
                "analysis": {"intent": "activate_mirror"}
            }
            
            response = await agent._process_mirror_command("mirror mirror", analysis_result)
            
            assert "mirror activated" in response.lower()
            agent.wedding_messages.execute.assert_called_with("welcome")
            
            # Check that mirror control was called twice (update_display and play_audio)
            assert agent.mirror_control.execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_process_mirror_command_compliment_request(self):
        """Test compliment request command processing"""
        with patch('agent2.google'), \
             patch('agent2.get_job_context'), \
             patch('agent2.Agent.__init__'):
            
            from agent2 import WeddingMirrorAssistant
            
            agent = WeddingMirrorAssistant()
            
            # Mock tool responses
            agent.image_compliments.execute = AsyncMock(return_value={
                "success": True,
                "compliment": "You look beautiful"
            })
            agent.mirror_control.execute = AsyncMock(return_value={
                "success": True
            })
            
            # Test compliment request
            analysis_result = {
                "analysis": {"intent": "request_compliment"}
            }
            
            response = await agent._process_mirror_command("give me a compliment", analysis_result)
            
            assert "compliment" in response.lower()
            agent.image_compliments.execute.assert_called_with("get_random_compliment")
            agent.mirror_control.execute.assert_called_with("update_display", message="You look beautiful")
    
    @pytest.mark.asyncio
    async def test_process_mirror_command_celebration_mode(self):
        """Test celebration mode command processing"""
        with patch('agent2.google'), \
             patch('agent2.get_job_context'), \
             patch('agent2.Agent.__init__'):
            
            from agent2 import WeddingMirrorAssistant
            
            agent = WeddingMirrorAssistant()
            
            # Mock tool responses
            agent.wedding_messages.execute = AsyncMock(return_value={
                "success": True,
                "message": "Let's celebrate!"
            })
            agent.mirror_control.execute = AsyncMock(return_value={
                "success": True
            })
            
            # Test celebration mode
            analysis_result = {
                "analysis": {"intent": "celebration_mode"}
            }
            
            response = await agent._process_mirror_command("let's party", analysis_result)
            
            assert "celebration" in response.lower()
            agent.wedding_messages.execute.assert_called_with("celebration")
            agent.mirror_control.execute.assert_called_with("update_display", message="Let's celebrate!")
    
    @pytest.mark.asyncio
    async def test_process_mirror_command_reset(self):
        """Test reset command processing"""
        with patch('agent2.google'), \
             patch('agent2.get_job_context'), \
             patch('agent2.Agent.__init__'):
            
            from agent2 import WeddingMirrorAssistant
            
            agent = WeddingMirrorAssistant()
            
            # Mock tool response
            agent.mirror_control.execute = AsyncMock(return_value={
                "success": True,
                "response": "Mirror reset"
            })
            
            # Test reset
            analysis_result = {
                "analysis": {"intent": "reset_mirror"}
            }
            
            response = await agent._process_mirror_command("reset", analysis_result)
            
            assert response == "Mirror reset"
            agent.mirror_control.execute.assert_called_with("reset")
    
    @pytest.mark.asyncio
    async def test_image_processing_workflow(self):
        """Test the complete image processing workflow"""
        with patch('agent2.google'), \
             patch('agent2.get_job_context'), \
             patch('agent2.Agent.__init__'):
            
            from agent2 import WeddingMirrorAssistant
            
            agent = WeddingMirrorAssistant()
            
            # Mock required attributes and methods
            agent.chat_ctx = MagicMock()
            agent.chat_ctx.copy.return_value = MagicMock()
            agent.update_chat_ctx = AsyncMock()
            
            # Mock tool responses
            agent.image_compliments.execute = AsyncMock(return_value={
                "success": True,
                "compliment": "You look stunning!",
                "analysis": {"style": "formal"}
            })
            agent.mirror_control.execute = AsyncMock(return_value={
                "success": True
            })
            
            # Mock reader
            mock_reader = MagicMock()
            mock_reader.info.name = "test_stream"
            mock_reader.__aiter__ = AsyncMock(return_value=iter([b"image", b"data"]))
            
            # Test image processing
            await agent._image_received_for_wedding(mock_reader, "test_participant")
            
            # Verify tool calls
            agent.image_compliments.execute.assert_called_once_with(
                "generate_compliment",
                image_data=b"imagedata",
                participant_id="test_participant"
            )
            agent.mirror_control.execute.assert_called_once_with(
                "update_display",
                message="You look stunning!"
            )
    
    @pytest.mark.asyncio
    async def test_voice_command_workflow(self):
        """Test the complete voice command processing workflow"""
        with patch('agent2.google'), \
             patch('agent2.get_job_context'), \
             patch('agent2.Agent.__init__'):
            
            from agent2 import WeddingMirrorAssistant
            
            agent = WeddingMirrorAssistant()
            
            # Mock required attributes and methods
            agent.chat_ctx = MagicMock()
            agent.chat_ctx.copy.return_value = MagicMock()
            agent.update_chat_ctx = AsyncMock()
            agent._process_mirror_command = AsyncMock(return_value="Command processed")
            
            # Mock tool response
            agent.guest_analysis.execute = AsyncMock(return_value={
                "success": True,
                "analysis": {"intent": "activate_mirror", "sentiment": "positive"}
            })
            
            # Mock reader
            mock_reader = MagicMock()
            mock_reader.info.name = "test_stream"
            mock_reader.__aiter__ = AsyncMock(return_value=iter([b"mirror mirror"]))
            
            # Test voice command processing
            await agent._voice_command_for_mirror(mock_reader, "test_participant")
            
            # Verify guest analysis was called
            agent.guest_analysis.execute.assert_called_once_with(
                "analyze_voice",
                command="mirror mirror",
                participant_id="test_participant"
            )


if __name__ == "__main__":
    pytest.main([__file__])