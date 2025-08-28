import openai
import os
from typing import Dict, Any

class IntroductionContentAgent:
    """
    AI agent that generates compelling introduction content for brand book presentations.
    Uses OpenAI/Claude to create professional, company-specific introduction text.
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.claude_api_key = os.getenv("CLAUDE_API_KEY")
        
        # Initialize OpenAI if available
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def generate_introduction(self, company_name: str, industry: str, 
                            values: str, audience: str, brand_essence: Dict = None) -> str:
        """
        Generate compelling introduction content for the brand book
        
        Args:
            company_name: Name of the company
            industry: Industry sector
            values: Company core values
            audience: Target audience description
            brand_essence: Brand essence data for context
            
        Returns:
            str: Formatted introduction text for the slide
        """
        
        # Prepare context from brand essence
        context = self._extract_brand_context(brand_essence)
        
        # Create the prompt for AI generation
        prompt = self._create_introduction_prompt(
            company_name, industry, values, audience, context
        )
        
        # Generate content using available AI
        if self.openai_api_key:
            print(f"🤖 Using OpenAI API to generate introduction for {company_name}")
            print(f"📝 Prompt preview: {prompt[:200]}...")
            return self._generate_with_openai(prompt)
        elif self.claude_api_key:
            print(f"🤖 Using Claude API to generate introduction for {company_name}")
            return self._generate_with_claude(prompt)
        else:
            print(f"⚠️ No AI API keys found, using fallback for {company_name}")
            print(f"💡 To enable AI generation, set OPENAI_API_KEY or CLAUDE_API_KEY in your .env file")
            return self._generate_fallback_introduction(company_name, industry, values)
    
    def _extract_brand_context(self, brand_essence: Dict) -> Dict:
        """Extract relevant context from brand essence for introduction"""
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
            
            # Market analysis insights
            market_analysis = brand_essence.get("market_analysis", {})
            context["industry_trends"] = market_analysis.get("industry_trends", [])[:3]
            
        return context
    
    def _create_introduction_prompt(self, company_name: str, industry: str, 
                                  values: str, audience: str, context: Dict) -> str:
        """Create AI prompt for introduction generation"""
        
        values_list = [v.strip() for v in values.split(',') if v.strip()]
        
        prompt = f"""Create a compelling introduction for {company_name}'s brand identity system presentation.

Company Details:
- Name: {company_name}
- Industry: {industry}
- Target Audience: {audience}
- Core Values: {', '.join(values_list)}

Additional Context:
- Brand Promise: {context.get('brand_promise', 'Not specified')}
- Unique Value Proposition: {context.get('unique_value_prop', 'Not specified')}
- Brand Personality: {', '.join(context.get('brand_personality', []))}

Requirements:
1. Write a professional, engaging introduction that explains the purpose of the brand identity system
2. Keep it concise but impactful (4-6 lines maximum)
3. Mention that this system ensures international, engaging, consistent, recognizable, and proprietary brand presentation
4. Reference the company's unique approach and fundamental principles
5. Use professional, confident tone suitable for stakeholders
6. Make it specific to {company_name} and {industry} industry
7. The text should flow naturally when presented on a slide

Format: Return only the introduction text, no additional formatting or explanations."""

        return prompt
    
    def _generate_with_openai(self, prompt: str) -> str:
        """Generate content using OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional brand strategist creating compelling brand book introductions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            generated_content = response.choices[0].message.content.strip()
            print(f"✅ OpenAI generated introduction: {generated_content[:100]}...")
            return generated_content
            
        except Exception as e:
            print(f"❌ OpenAI generation failed: {e}")
            return self._generate_fallback_introduction_from_prompt(prompt)
    
    def _generate_with_claude(self, prompt: str) -> str:
        """Generate content using Claude API (placeholder for future implementation)"""
        # This would implement Claude API integration
        # For now, fall back to template
        return self._generate_fallback_introduction_from_prompt(prompt)
    
    def _generate_fallback_introduction(self, company_name: str, industry: str, values: str) -> str:
        """Generate fallback introduction when AI is not available"""
        values_list = [v.strip() for v in values.split(',') if v.strip()]
        
        if industry.lower() in ['technology', 'tech', 'software']:
            return f"""The following brand identity system for {company_name}
is thoughtfully crafted to present our brand in
an international, engaging, consistent, recognizable
and proprietary way. Rooted in {values_list[0].lower()} and driven by
innovation, our system reflects our commitment to excellence."""
        
        elif industry.lower() in ['healthcare', 'medical', 'health']:
            return f"""The following brand identity system for {company_name}
is thoughtfully crafted to present our brand in
an international, engaging, consistent, recognizable
and proprietary way. Built on trust and {values_list[0].lower()}, our
system embodies our dedication to improving lives."""
        
        elif industry.lower() in ['finance', 'financial', 'banking']:
            return f"""The following brand identity system for {company_name}
is thoughtfully crafted to present our brand in
an international, engaging, consistent, recognizable
and proprietary way. Grounded in {values_list[0].lower()} and integrity,
our system reflects our commitment to financial excellence."""
        
        else:
            # Generic industry-agnostic introduction
            return f"""The following brand identity system for {company_name}
is thoughtfully crafted to present our brand in
an international, engaging, consistent, recognizable
and proprietary way. Unique in form, versatile in its
application and unified by our fundamental principles."""
    
    def _generate_fallback_introduction_from_prompt(self, prompt: str) -> str:
        """Extract company name from prompt and generate basic introduction"""
        # Simple fallback that extracts company name from prompt
        lines = prompt.split('\n')
        company_name = "your organization"
        
        for line in lines:
            if line.startswith("- Name:"):
                company_name = line.replace("- Name:", "").strip()
                break
        
        return f"""The following brand identity system for {company_name}
is thoughtfully crafted to present our brand in
an international, engaging, consistent, recognizable
and proprietary way. Unique in form, versatile in its
application and unified by a fundamental principle."""

# Example usage and testing
if __name__ == "__main__":
    agent = IntroductionContentAgent()
    
    # Test data
    test_company = "TechForward Inc"
    test_industry = "Technology"
    test_values = "Innovation, Simplicity, Human-Centered"
    test_audience = "Progressive businesses seeking digital transformation"
    
    test_brand_essence = {
        "brand_positioning": {
            "unique_value_proposition": "We bridge the gap between complex technology and intuitive user experiences",
            "brand_promise": "Technology that works for you, not against you",
            "brand_personality": ["Innovative", "Reliable", "Approachable"]
        }
    }
    
    introduction = agent.generate_introduction(
        test_company, test_industry, test_values, test_audience, test_brand_essence
    )
    
    print("Generated Introduction:")
    print(introduction)