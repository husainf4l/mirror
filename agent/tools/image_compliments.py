import random
import asyncio
import base64
from typing import Dict, Any, List, Optional
from .base_tool import BaseTool


class ImageComplimentsTool(BaseTool):
    """Tool for generating personalized compliments based on image analysis"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compliment_templates = [
            '<span class="line script">You look</span><span class="line fancy">Absolutely Radiant</span><span class="line script">tonight</span>',
            '<span class="line fancy">Stunning</span><span class="line script">as always</span><span class="line fancy">Beautiful Guest</span>',
            '<span class="line script">Your beauty</span><span class="line fancy">Lights Up</span><span class="line script">this celebration</span>',
            '<span class="line fancy">Elegant</span><span class="line script">and</span><span class="line fancy">Magnificent</span>',
            '<span class="line script">Pure</span><span class="line fancy">Grace & Beauty</span><span class="line script">personified</span>',
            '<span class="line fancy">Breathtaking</span><span class="line script">in every</span><span class="line fancy">Way</span>',
            '<span class="line script">Simply</span><span class="line fancy">Gorgeous</span><span class="line script">tonight</span>',
            '<span class="line fancy">Radiant Beauty</span><span class="line script">shines</span><span class="line fancy">Bright</span>',
            '<span class="line script">You are</span><span class="line fancy">Absolutely</span><span class="line script">Stunning</span>',
            '<span class="line fancy">Perfect</span><span class="line script">elegance</span><span class="line fancy">Personified</span>'
        ]
        
        self.style_based_compliments = {
            "formal": [
                '<span class="line script">Exquisite</span><span class="line fancy">Formal Elegance</span><span class="line script">tonight</span>',
                '<span class="line fancy">Distinguished</span><span class="line script">and</span><span class="line fancy">Refined</span>'
            ],
            "colorful": [
                '<span class="line script">Beautiful</span><span class="line fancy">Colors</span><span class="line script">suit you perfectly</span>',
                '<span class="line fancy">Vibrant</span><span class="line script">and</span><span class="line fancy">Stunning</span>'
            ],
            "group": [
                '<span class="line fancy">Beautiful</span><span class="line script">group of</span><span class="line fancy">Amazing People</span>',
                '<span class="line script">What a</span><span class="line fancy">Wonderful</span><span class="line script">gathering</span>'
            ]
        }
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute image compliment actions"""
        self._log_execution("ImageCompliments", f"Action: {action}")
        
        if action == "generate_compliment":
            return await self._generate_compliment(
                kwargs.get("image_data"), 
                kwargs.get("participant_id", ""),
                kwargs.get("style_hint", "")
            )
        elif action == "analyze_image":
            return await self._analyze_image(kwargs.get("image_data"))
        elif action == "get_random_compliment":
            return await self._get_random_compliment()
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    async def _generate_compliment(self, image_data: Optional[bytes], participant_id: str, style_hint: str = "") -> Dict[str, Any]:
        """Generate a personalized compliment based on image analysis"""
        await asyncio.sleep(0.2)  # Simulate AI processing time
        
        # Simulate image analysis
        analysis = await self._analyze_image(image_data) if image_data else {}
        
        # Select compliment based on analysis or style hint
        compliment = self._select_compliment(analysis.get("style", ""), style_hint)
        
        return {
            "success": True,
            "compliment": compliment,
            "participant_id": participant_id,
            "analysis": analysis,
            "response": f"Personalized compliment generated for {participant_id}"
        }
    
    async def _analyze_image(self, image_data: Optional[bytes]) -> Dict[str, Any]:
        """Analyze image for style and characteristics (mock implementation)"""
        if not image_data:
            return {"style": "general", "confidence": 0.5}
        
        await asyncio.sleep(0.1)  # Simulate processing
        
        # Mock analysis - in real implementation, this would use computer vision
        analysis = {
            "style": random.choice(["formal", "colorful", "group", "general"]),
            "people_count": random.randint(1, 5),
            "lighting": random.choice(["bright", "dim", "natural"]),
            "setting": random.choice(["indoor", "outdoor", "mixed"]),
            "confidence": random.uniform(0.7, 0.95)
        }
        
        return analysis
    
    def _select_compliment(self, analyzed_style: str, style_hint: str) -> str:
        """Select appropriate compliment based on analysis and hints"""
        # Prioritize style hint, then analysis, then random
        style = style_hint or analyzed_style or "general"
        
        if style in self.style_based_compliments:
            compliments = self.style_based_compliments[style] + self.compliment_templates
        else:
            compliments = self.compliment_templates
        
        return random.choice(compliments)
    
    async def _get_random_compliment(self) -> Dict[str, Any]:
        """Get a random compliment without image analysis"""
        compliment = random.choice(self.compliment_templates)
        return {
            "success": True,
            "compliment": compliment,
            "type": "random",
            "response": "Random compliment generated"
        }
    
    def add_custom_compliment(self, compliment: str, style: str = "general") -> bool:
        """Add a custom compliment template"""
        try:
            if style == "general":
                self.compliment_templates.append(compliment)
            else:
                if style not in self.style_based_compliments:
                    self.style_based_compliments[style] = []
                self.style_based_compliments[style].append(compliment)
            return True
        except Exception as e:
            self.logger.error(f"Failed to add custom compliment: {e}")
            return False