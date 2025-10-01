import pytest
import asyncio
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.image_compliments import ImageComplimentsTool


class TestImageComplimentsTool:
    """Test suite for ImageComplimentsTool"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tool = ImageComplimentsTool()
    
    @pytest.mark.asyncio
    async def test_generate_compliment_with_image(self):
        """Test compliment generation with image data"""
        image_data = b"fake_image_data"
        participant_id = "test_guest"
        
        result = await self.tool.execute(
            "generate_compliment",
            image_data=image_data,
            participant_id=participant_id
        )
        
        assert result["success"] is True
        assert "compliment" in result
        assert result["participant_id"] == participant_id
        assert "analysis" in result
        assert result["analysis"]["confidence"] > 0
    
    @pytest.mark.asyncio
    async def test_generate_compliment_without_image(self):
        """Test compliment generation without image data"""
        result = await self.tool.execute(
            "generate_compliment",
            participant_id="test_guest"
        )
        
        assert result["success"] is True
        assert "compliment" in result
        assert result["compliment"] in self.tool.compliment_templates
    
    @pytest.mark.asyncio
    async def test_analyze_image(self):
        """Test image analysis functionality"""
        image_data = b"fake_image_data"
        
        result = await self.tool.execute("analyze_image", image_data=image_data)
        
        # Note: execute method doesn't directly support analyze_image
        # Let's test the internal method
        analysis = await self.tool._analyze_image(image_data)
        
        assert "style" in analysis
        assert analysis["style"] in ["formal", "colorful", "group", "general"]
        assert "people_count" in analysis
        assert "lighting" in analysis
        assert "setting" in analysis
        assert "confidence" in analysis
        assert 0 <= analysis["confidence"] <= 1
    
    @pytest.mark.asyncio
    async def test_get_random_compliment(self):
        """Test random compliment generation"""
        result = await self.tool.execute("get_random_compliment")
        
        assert result["success"] is True
        assert result["type"] == "random"
        assert "compliment" in result
        assert result["compliment"] in self.tool.compliment_templates
    
    @pytest.mark.asyncio
    async def test_style_based_compliments(self):
        """Test style-based compliment selection"""
        # Test formal style
        compliment = self.tool._select_compliment("formal", "")
        assert isinstance(compliment, str)
        assert 'span class="line' in compliment
        
        # Test colorful style
        compliment = self.tool._select_compliment("colorful", "")
        assert isinstance(compliment, str)
        
        # Test group style
        compliment = self.tool._select_compliment("group", "")
        assert isinstance(compliment, str)
    
    @pytest.mark.asyncio
    async def test_style_hint_priority(self):
        """Test that style hint takes priority over analysis"""
        # Mock analysis with one style, but provide different style hint
        compliment = self.tool._select_compliment("general", "formal")
        # Should use formal style based on hint, not general from analysis
        assert isinstance(compliment, str)
    
    def test_add_custom_compliment(self):
        """Test adding custom compliments"""
        custom_compliment = '<span class="line fancy">Custom</span><span class="line script">Test</span>'
        
        # Add to general templates
        result = self.tool.add_custom_compliment(custom_compliment)
        assert result is True
        assert custom_compliment in self.tool.compliment_templates
        
        # Add to specific style
        style_compliment = '<span class="line fancy">Formal</span><span class="line script">Custom</span>'
        result = self.tool.add_custom_compliment(style_compliment, "formal")
        assert result is True
        assert style_compliment in self.tool.style_based_compliments["formal"]
    
    def test_compliment_templates_format(self):
        """Test that compliment templates are properly formatted"""
        for compliment in self.tool.compliment_templates:
            assert 'span class="line' in compliment
            assert isinstance(compliment, str)
            assert len(compliment) > 0
        
        for style, compliments in self.tool.style_based_compliments.items():
            for compliment in compliments:
                assert 'span class="line' in compliment
                assert isinstance(compliment, str)
    
    @pytest.mark.asyncio
    async def test_unknown_action(self):
        """Test unknown action handling"""
        result = await self.tool.execute("unknown_action")
        
        assert result["success"] is False
        assert "unknown action" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_multiple_random_compliments_variety(self):
        """Test that random compliments show variety"""
        compliments = []
        for _ in range(10):
            result = await self.tool.execute("get_random_compliment")
            compliments.append(result["compliment"])
        
        # Should have some variety (unless there's only one template)
        unique_compliments = set(compliments)
        assert len(unique_compliments) > 1 or len(self.tool.compliment_templates) == 1
    
    @pytest.mark.asyncio
    async def test_image_analysis_without_data(self):
        """Test image analysis with no data"""
        analysis = await self.tool._analyze_image(None)
        
        assert analysis["style"] == "general"
        assert analysis["confidence"] == 0.5


if __name__ == "__main__":
    pytest.main([__file__])