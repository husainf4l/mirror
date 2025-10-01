import pytest
import asyncio
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.guest_analysis import GuestAnalysisTool


class TestGuestAnalysisTool:
    """Test suite for GuestAnalysisTool"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tool = GuestAnalysisTool()
    
    @pytest.mark.asyncio
    async def test_analyze_voice_command(self):
        """Test voice command analysis"""
        result = await self.tool.execute(
            "analyze_voice",
            command="Mirror mirror on the wall",
            participant_id="guest1"
        )
        
        assert result["success"] is True
        assert "analysis" in result
        analysis = result["analysis"]
        assert analysis["participant_id"] == "guest1"
        assert analysis["command"] == "Mirror mirror on the wall"
        assert analysis["intent"] == "activate_mirror"
        assert analysis["sentiment"] in ["positive", "negative", "neutral"]
    
    @pytest.mark.asyncio
    async def test_intent_extraction(self):
        """Test intent extraction from various commands"""
        test_cases = [
            ("mirror mirror", "activate_mirror"),
            ("you look beautiful", "request_compliment"),
            ("let's celebrate", "celebration_mode"),
            ("reset the mirror", "reset_mirror"),
            ("take a photo", "take_photo"),
            ("hello there", "general_interaction")
        ]
        
        for command, expected_intent in test_cases:
            result = await self.tool.execute(
                "analyze_voice",
                command=command,
                participant_id="test_guest"
            )
            assert result["analysis"]["intent"] == expected_intent
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis(self):
        """Test sentiment analysis"""
        test_cases = [
            ("I love this beautiful celebration", "positive"),
            ("This is amazing and wonderful", "positive"),
            ("I'm sad and upset", "negative"),
            ("Hello there", "neutral")
        ]
        
        for command, expected_sentiment in test_cases:
            result = await self.tool.execute(
                "analyze_voice",
                command=command,
                participant_id="test_guest"
            )
            assert result["analysis"]["sentiment"] == expected_sentiment
    
    @pytest.mark.asyncio
    async def test_guest_profile_creation(self):
        """Test guest profile creation and retrieval"""
        participant_id = "new_guest"
        
        # Analyze a command to create guest data
        await self.tool.execute(
            "analyze_voice",
            command="mirror mirror",
            participant_id=participant_id
        )
        
        # Get guest profile
        result = await self.tool.execute("get_guest_profile", participant_id=participant_id)
        
        assert result["success"] is True
        assert result["participant_id"] == participant_id
        profile = result["profile"]
        assert "interactions" in profile
        assert len(profile["interactions"]) == 1
        assert profile["interactions"][0]["command"] == "mirror mirror"
        assert profile["interactions"][0]["intent"] == "activate_mirror"
    
    @pytest.mark.asyncio
    async def test_update_guest_info(self):
        """Test updating guest information"""
        participant_id = "guest_to_update"
        update_info = {"name": "John", "preferences": {"compliment_style": "elegant"}}
        
        result = await self.tool.execute(
            "update_guest_info",
            participant_id=participant_id,
            info=update_info
        )
        
        assert result["success"] is True
        assert result["participant_id"] == participant_id
        assert result["updated_info"] == update_info
        
        # Verify the update
        profile_result = await self.tool.execute("get_guest_profile", participant_id=participant_id)
        profile = profile_result["profile"]
        assert profile["name"] == "John"
        assert profile["preferences"]["compliment_style"] == "elegant"
    
    @pytest.mark.asyncio
    async def test_multiple_interactions_tracking(self):
        """Test tracking multiple interactions for same guest"""
        participant_id = "frequent_guest"
        commands = ["mirror mirror", "you look beautiful", "let's celebrate"]
        
        # Execute multiple commands
        for command in commands:
            await self.tool.execute(
                "analyze_voice",
                command=command,
                participant_id=participant_id
            )
        
        # Check interaction history
        result = await self.tool.execute("get_guest_profile", participant_id=participant_id)
        profile = result["profile"]
        
        assert len(profile["interactions"]) == len(commands)
        recorded_commands = [interaction["command"] for interaction in profile["interactions"]]
        assert recorded_commands == commands
    
    @pytest.mark.asyncio
    async def test_unknown_action(self):
        """Test unknown action handling"""
        result = await self.tool.execute("unknown_action")
        
        assert result["success"] is False
        assert "unknown action" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_empty_profile_retrieval(self):
        """Test retrieving profile for non-existent guest"""
        result = await self.tool.execute("get_guest_profile", participant_id="non_existent")
        
        assert result["success"] is True
        profile = result["profile"]
        assert "interactions" in profile
        assert len(profile["interactions"]) == 0
        assert "preferences" in profile
        assert "first_seen" in profile


if __name__ == "__main__":
    pytest.main([__file__])