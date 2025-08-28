import openai
import os
from typing import Dict, Any

class BrandStoryContentAgent:
    """
    AI agent that generates compelling brand story content for brand book presentations.
    Creates narrative-driven brand stories using OpenAI/Claude that connect with audiences.
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.claude_api_key = os.getenv("CLAUDE_API_KEY")
        
        # Initialize OpenAI if available
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def generate_brand_story(self, company_name: str, industry: str, 
                           values: str, audience: str, brand_essence: Dict = None,
                           literature_data: Dict = None) -> str:
        """
        Generate compelling brand story content
        
        Args:
            company_name: Name of the company
            industry: Industry sector
            values: Company core values
            audience: Target audience description
            brand_essence: Brand essence data for context
            literature_data: Existing literature data if available
            
        Returns:
            str: Formatted brand story text for the slide
        """
        
        # Check if brand story already exists in literature_data
        if literature_data and literature_data.get("brand_story"):
            existing_story = literature_data["brand_story"]
            if len(existing_story.strip()) > 50:  # Use existing if substantial
                return self._format_existing_story(existing_story, company_name)
        
        # Prepare context from brand essence
        context = self._extract_brand_context(brand_essence)
        
        # Create the prompt for AI generation
        prompt = self._create_brand_story_prompt(
            company_name, industry, values, audience, context
        )
        
        # Generate content using available AI
        if self.openai_api_key:
            return self._generate_with_openai(prompt, company_name)
        elif self.claude_api_key:
            return self._generate_with_claude(prompt, company_name)
        else:
            return self._generate_fallback_story(company_name, industry, values)
    
    def _format_existing_story(self, existing_story: str, company_name: str) -> str:
        """Format existing brand story for slide presentation"""
        # Clean and format the existing story
        story = existing_story.strip()
        
        # Ensure it's not too long for a slide (aim for ~150-200 words)
        words = story.split()
        if len(words) > 200:
            # Truncate and add proper ending
            story = ' '.join(words[:200]) + "..."
        
        # Ensure it has proper paragraph breaks for slide readability
        if '\n\n' not in story:
            # Add paragraph breaks at sentence boundaries for readability
            sentences = story.split('. ')
            if len(sentences) > 4:
                mid_point = len(sentences) // 2
                story = '. '.join(sentences[:mid_point]) + '.\n\n' + '. '.join(sentences[mid_point:])
        
        return story
    
    def _extract_brand_context(self, brand_essence: Dict) -> Dict:
        """Extract relevant context from brand essence for brand story"""
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
            competitor_insights = market_analysis.get("competitor_insights", {})
            context["market_gap"] = competitor_insights.get("market_gap", "")
            
        return context
    
    def _create_brand_story_prompt(self, company_name: str, industry: str, 
                                 values: str, audience: str, context: Dict) -> str:
        """Create AI prompt for brand story generation"""
        
        values_list = [v.strip() for v in values.split(',') if v.strip()]
        
        prompt = f"""Create a compelling brand story for {company_name} that will appear in their brand book presentation.

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
- Market Gap: {context.get('market_gap', 'Not specified')}

Story Requirements:
1. Write a narrative that explains the company's origin, mission, and vision
2. Make it engaging and relatable to {audience}
3. Incorporate the core values naturally into the narrative
4. Show what makes {company_name} unique in the {industry} industry
5. Keep it concise but impactful (150-200 words maximum)
6. Use professional yet human tone
7. Focus on the "why" behind the company's existence
8. Include the company's impact on customers/industry
9. End with a forward-looking statement about the future

Story Structure:
- Opening: Set the scene or challenge that led to the company's creation
- Journey: How the company was built and evolved
- Values in action: Show how core values drive decisions
- Impact: What the company achieves for customers/society
- Future vision: Where the company is heading

Write only the story content, no additional formatting or explanations. Make it slide-ready."""

        return prompt
    
    def _generate_with_openai(self, prompt: str, company_name: str) -> str:
        """Generate content using OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional brand storyteller creating compelling company narratives. Focus on authenticity, emotional connection, and business relevance."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.8
            )
            
            story = response.choices[0].message.content.strip()
            print(f"✅ OpenAI generated brand story: {story[:100]}...")
            return self._format_story_for_slide(story)
            
        except Exception as e:
            print(f"❌ OpenAI generation failed: {e}")
            return self._generate_fallback_story(company_name, "technology", "innovation, quality, service")
    
    def _generate_with_claude(self, prompt: str, company_name: str) -> str:
        """Generate content using Claude API (placeholder for future implementation)"""
        # This would implement Claude API integration
        # For now, fall back to template
        return self._generate_fallback_story(company_name, "technology", "innovation, quality, service")
    
    def _format_story_for_slide(self, story: str) -> str:
        """Format AI-generated story for slide presentation"""
        # Clean up the story
        story = story.strip()
        
        # Remove any unwanted formatting
        story = story.replace("**", "").replace("*", "")
        
        # Ensure proper paragraph breaks for slide readability
        if '\n\n' not in story and len(story.split()) > 50:
            sentences = story.split('. ')
            if len(sentences) > 3:
                mid_point = len(sentences) // 2
                story = '. '.join(sentences[:mid_point]) + '.\n\n' + '. '.join(sentences[mid_point:])
        
        return story
    
    def _generate_fallback_story(self, company_name: str, industry: str, values: str) -> str:
        """Generate fallback brand story when AI is not available"""
        values_list = [v.strip() for v in values.split(',') if v.strip()]
        primary_value = values_list[0] if values_list else "excellence"
        
        # Industry-specific story templates
        if industry.lower() in ['technology', 'tech', 'software']:
            story = f"""Founded on the belief that technology should enhance human potential, {company_name} emerged from a simple yet powerful vision: to bridge the gap between complex innovation and everyday usability.

Our journey began when we recognized that the {industry} landscape was filled with solutions that prioritized features over user experience. Driven by {primary_value.lower()} and guided by our core values, we set out to create technology that truly serves its users.

Today, {company_name} stands as a testament to what happens when cutting-edge innovation meets human-centered design. We don't just build products; we craft experiences that empower our clients to achieve their goals more effectively. Our commitment to {', '.join(values_list[:2])} continues to drive every decision we make, ensuring that our solutions not only meet today's needs but anticipate tomorrow's challenges."""

        elif industry.lower() in ['healthcare', 'medical', 'health']:
            story = f"""The story of {company_name} began with a profound realization: healthcare should heal, not burden. Founded by professionals who witnessed firsthand the complexities facing both patients and providers, our company was born from a commitment to transform healthcare delivery.

Our founders believed that {primary_value.lower()} in healthcare wasn't just an aspiration—it was a necessity. This conviction, supported by our values of {', '.join(values_list)}, became the foundation upon which we built our mission.

Through innovative solutions and unwavering dedication to improving patient outcomes, {company_name} has grown into a trusted partner for healthcare organizations worldwide. We continue to push boundaries, ensuring that quality care remains accessible and that healthcare professionals have the tools they need to make a meaningful difference in people's lives."""

        elif industry.lower() in ['finance', 'financial', 'banking']:
            story = f"""In a world where financial complexity often overshadows financial opportunity, {company_name} was founded on a revolutionary premise: that everyone deserves access to clear, trustworthy, and empowering financial solutions.

Our story began when our founders recognized that traditional financial services were failing to serve the evolving needs of modern businesses and individuals. Committed to {primary_value.lower()} and driven by values of {', '.join(values_list)}, we set out to democratize financial success.

Today, {company_name} stands at the forefront of financial innovation, providing solutions that not only meet our clients' immediate needs but also empower them to build stronger financial futures. Our dedication to transparency and client success continues to guide our growth as we expand our impact across the financial landscape."""

        else:
            # Generic industry-agnostic story
            story = f"""The vision for {company_name} was born from a simple observation: our industry needed a partner who truly understood the challenges facing modern businesses. Founded on principles of {primary_value.lower()} and integrity, our company emerged to fill this critical gap.

Our journey began with a commitment to doing business differently. Rather than following conventional approaches, we chose to listen deeply to our clients' needs and craft solutions that address their real-world challenges. This philosophy, rooted in our values of {', '.join(values_list)}, has become the cornerstone of our success.

As we continue to grow, {company_name} remains dedicated to delivering exceptional value and building lasting partnerships. Our story is still being written, with each client relationship and innovative solution adding new chapters to our mission of driving meaningful progress in the {industry} industry."""

        return story

# Example usage and testing
if __name__ == "__main__":
    agent = BrandStoryContentAgent()
    
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
        },
        "market_analysis": {
            "competitor_insights": {
                "market_gap": "Lack of user-friendly technology solutions in enterprise market"
            }
        }
    }
    
    story = agent.generate_brand_story(
        test_company, test_industry, test_values, test_audience, test_brand_essence
    )
    
    print("Generated Brand Story:")
    print(story)