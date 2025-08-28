import openai
import os
from typing import Dict, Any

class BrandPurposeContentAgent:
    """
    AI agent that generates compelling brand purpose content for brand book presentations.
    Creates mission, vision, and core values content using OpenAI/Claude.
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.claude_api_key = os.getenv("CLAUDE_API_KEY")
        
        # Initialize OpenAI if available
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def generate_brand_purpose(self, company_name: str, industry: str, 
                             values: str, audience: str, brand_essence: Dict = None) -> Dict[str, str]:
        """
        Generate comprehensive brand purpose content
        
        Args:
            company_name: Name of the company
            industry: Industry sector
            values: Company core values
            audience: Target audience description
            brand_essence: Brand essence data for context
            
        Returns:
            Dict containing vision, mission, and formatted values content
        """
        
        # Prepare context from brand essence
        context = self._extract_brand_context(brand_essence)
        
        # Create the prompt for AI generation
        prompt = self._create_brand_purpose_prompt(
            company_name, industry, values, audience, context
        )
        
        # Generate content using available AI
        if self.openai_api_key:
            print(f"🤖 Using OpenAI API to generate brand purpose for {company_name}")
            return self._generate_with_openai(prompt, company_name, values)
        elif self.claude_api_key:
            print(f"🤖 Using Claude API to generate brand purpose for {company_name}")
            return self._generate_with_claude(prompt, company_name, values)
        else:
            print(f"⚠️ No AI API keys found, using fallback for brand purpose for {company_name}")
            return self._generate_fallback_purpose(company_name, industry, values)
    
    def _extract_brand_context(self, brand_essence: Dict) -> Dict:
        """Extract relevant context from brand essence for brand purpose"""
        context = {}
        
        if brand_essence:
            # Company profile context
            company_profile = brand_essence.get("company_profile", {})
            context["core_values"] = company_profile.get("core_values", [])
            context["target_audience"] = company_profile.get("target_audience", "")
            
            # Brand positioning context
            brand_positioning = brand_essence.get("brand_positioning", {})
            context["unique_value_prop"] = brand_positioning.get("unique_value_proposition", "")
            context["brand_promise"] = brand_positioning.get("brand_promise", "")
            context["brand_personality"] = brand_positioning.get("brand_personality", [])
            context["competitive_advantage"] = brand_positioning.get("competitive_advantage", "")
            
            # Market analysis insights
            market_analysis = brand_essence.get("market_analysis", {})
            context["industry_trends"] = market_analysis.get("industry_trends", [])[:3]
            
        return context
    
    def _create_brand_purpose_prompt(self, company_name: str, industry: str, 
                                   values: str, audience: str, context: Dict) -> str:
        """Create AI prompt for brand purpose generation"""
        
        values_list = [v.strip() for v in values.split(',') if v.strip()]
        
        prompt = f"""Create compelling brand purpose content for {company_name}'s brand book presentation.

Company Details:
- Name: {company_name}
- Industry: {industry}
- Target Audience: {audience}
- Core Values: {', '.join(values_list)}

Brand Context:
- Brand Promise: {context.get('brand_promise', 'Not specified')}
- Unique Value Proposition: {context.get('unique_value_prop', 'Not specified')}
- Brand Personality: {', '.join(context.get('brand_personality', []))}
- Competitive Advantage: {context.get('competitive_advantage', 'Not specified')}

Generate the following sections:

1. VISION STATEMENT:
   - Forward-looking aspirational statement (1-2 sentences)
   - Should reflect the company's ultimate goal or desired future impact
   - Inspiring and motivational for {audience}

2. MISSION STATEMENT:
   - Clear statement of what the company does and why (1-2 sentences)
   - Should be actionable and specific to {industry} industry
   - Focus on current purpose and core business

3. CORE VALUES PARAGRAPH:
   - Take the provided values: {', '.join(values_list)}
   - Create a flowing paragraph that naturally incorporates all the values
   - Make it relevant to {industry} and {audience}
   - Write it as a cohesive narrative, not bullet points
   - Keep it to 3-4 sentences maximum to fit slide layout

IMPORTANT: 
- Format the entire response as flowing paragraphs, NOT bullet points
- Keep total content to 8-10 lines maximum to fit on slide
- Make it cohesive and narrative-driven
- Each section should flow naturally into the next

Requirements:
- Professional yet inspiring tone
- Industry-specific language for {industry}
- Relevant to {audience}
- Concise but impactful (8-10 lines total)
- Paragraph format, no bullet points
- Align with the brand promise and competitive advantage

Format your response as flowing paragraphs:
VISION: [vision statement paragraph]

MISSION: [mission statement paragraph]

VALUES: [flowing paragraph incorporating all core values naturally]"""

        return prompt
    
    def _generate_with_openai(self, prompt: str, company_name: str, values: str) -> Dict[str, str]:
        """Generate content using OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional brand strategist creating compelling brand purpose statements. Focus on clarity, inspiration, and business relevance."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            print(f"✅ OpenAI generated brand purpose: {content[:100]}...")
            return self._parse_ai_response(content, company_name, values)
            
        except Exception as e:
            print(f"❌ OpenAI generation failed: {e}")
            return self._generate_fallback_purpose(company_name, "technology", values)
    
    def _generate_with_claude(self, prompt: str, company_name: str, values: str) -> Dict[str, str]:
        """Generate content using Claude API (placeholder for future implementation)"""
        # This would implement Claude API integration
        # For now, fall back to template
        return self._generate_fallback_purpose(company_name, "technology", values)
    
    def _parse_ai_response(self, content: str, company_name: str, values: str) -> Dict[str, str]:
        """Parse AI response into structured format"""
        result = {
            "vision": "",
            "mission": "",
            "values_content": "",
            "full_content": ""
        }
        
        lines = content.split('\n')
        current_section = None
        
        vision_text = ""
        mission_text = ""
        values_text = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("VISION:"):
                current_section = "vision"
                vision_text = line.replace("VISION:", "").strip()
            elif line.startswith("MISSION:"):
                current_section = "mission"
                mission_text = line.replace("MISSION:", "").strip()
            elif line.startswith("VALUES:"):
                current_section = "values"
                values_text = line.replace("VALUES:", "").strip()
            elif current_section and line:
                if current_section == "vision":
                    vision_text += " " + line
                elif current_section == "mission":
                    mission_text += " " + line
                elif current_section == "values":
                    values_text += " " + line
        
        result["vision"] = vision_text.strip()
        result["mission"] = mission_text.strip()
        result["values_content"] = values_text.strip()
        
        # Create full formatted content for slide (without "Our Purpose" title)
        full_content = ""
        if result["vision"]:
            full_content += f"Vision: {result['vision']}\n\n"
        if result["mission"]:
            full_content += f"Mission: {result['mission']}\n\n"
        if result["values_content"]:
            full_content += f"Core Values: {result['values_content']}"
        else:
            # Fallback if values parsing failed - create paragraph format
            values_list = [v.strip() for v in values.split(',') if v.strip()]
            if values_list:
                values_paragraph = f"Our core values of {', '.join(values_list[:-1])} and {values_list[-1]} guide everything we do, from innovation to customer service excellence."
                full_content += f"Core Values: {values_paragraph}"
        
        # Remove the "Our Purpose" title if it exists at the beginning
        if full_content.startswith("Our Purpose\n\n"):
            full_content = full_content[12:]  # Remove "Our Purpose\n\n"
        
        result["full_content"] = full_content.strip()
        return result
    
    def _generate_fallback_purpose(self, company_name: str, industry: str, values: str) -> Dict[str, str]:
        """Generate fallback brand purpose when AI is not available"""
        values_list = [v.strip() for v in values.split(',') if v.strip()]
        
        # Industry-specific templates
        if industry.lower() in ['technology', 'tech', 'software']:
            vision = f"To be the leading force in technological innovation that empowers businesses and individuals to achieve their full potential."
            mission = f"We create cutting-edge technology solutions that simplify complex challenges and drive meaningful progress for our clients."
        
        elif industry.lower() in ['healthcare', 'medical', 'health']:
            vision = f"To transform healthcare delivery and improve quality of life for communities worldwide."
            mission = f"We provide innovative healthcare solutions that enhance patient care and support medical professionals in their vital work."
        
        elif industry.lower() in ['finance', 'financial', 'banking']:
            vision = f"To democratize financial success and create a world where everyone has access to smart financial solutions."
            mission = f"We deliver trusted financial services that empower individuals and businesses to build secure and prosperous futures."
        
        elif industry.lower() in ['education', 'learning']:
            vision = f"To unlock human potential through transformative learning experiences that inspire lifelong growth."
            mission = f"We create innovative educational solutions that make learning accessible, engaging, and impactful for learners everywhere."
        
        else:
            # Generic industry-agnostic purpose
            vision = f"To be the preferred partner for businesses seeking excellence and innovation in their field."
            mission = f"We deliver exceptional solutions that drive growth and create lasting value for our clients and communities."
        
        # Create values content as flowing paragraph
        if len(values_list) > 0:
            if len(values_list) == 1:
                values_content = f"Core Values: Our commitment to {values_list[0].lower()} drives every decision we make and shapes how we serve our clients and community."
            elif len(values_list) == 2:
                values_content = f"Core Values: Through {values_list[0].lower()} and {values_list[1].lower()}, we build lasting relationships and deliver exceptional value to all our stakeholders."
            else:
                # For 3 or more values, create a flowing paragraph
                values_content = f"Core Values: Our foundation rests on {values_list[0].lower()}, {', '.join([v.lower() for v in values_list[1:-1]])}, and {values_list[-1].lower()}, which together guide our commitment to excellence and drive our mission to create meaningful impact for our clients."
        else:
            values_content = "Core Values: Our principles guide everything we do, from innovation to customer service excellence."
        
        # Create full content (without "Our Purpose" title)
        full_content = f"""Vision: {vision}

Mission: {mission}

{values_content}"""
        
        return {
            "vision": vision,
            "mission": mission, 
            "values_content": values_content,
            "full_content": full_content
        }

# Example usage and testing
if __name__ == "__main__":
    agent = BrandPurposeContentAgent()
    
    # Test data
    test_company = "TechForward Inc"
    test_industry = "Technology"
    test_values = "Innovation, Simplicity, Human-Centered"
    test_audience = "Progressive businesses seeking digital transformation"
    
    test_brand_essence = {
        "brand_positioning": {
            "unique_value_proposition": "We bridge the gap between complex technology and intuitive user experiences",
            "brand_promise": "Technology that works for you, not against you",
            "brand_personality": ["Innovative", "Reliable", "Approachable"],
            "competitive_advantage": "Deep understanding of human psychology drives more intuitive solutions"
        }
    }
    
    purpose_content = agent.generate_brand_purpose(
        test_company, test_industry, test_values, test_audience, test_brand_essence
    )
    
    print("Generated Brand Purpose:")
    print(purpose_content["full_content"])