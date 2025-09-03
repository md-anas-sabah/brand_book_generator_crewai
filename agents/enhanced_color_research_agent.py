import openai
import os
import requests
import json
from typing import Dict, List, Any, Tuple
import colorsys
import re
from dotenv import load_dotenv

load_dotenv()

class EnhancedColorResearchAgent:
    """
    AI agent that generates comprehensive color palettes with industry research and detailed specifications.
    Creates primary colors (3-4), secondary colors (5), and usage guidelines based on company context.
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.claude_api_key = os.getenv("CLAUDE_API_KEY")
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        
        # Initialize OpenAI if available
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def generate_comprehensive_color_system(self, company_name: str, industry: str, 
                                          values: str, audience: str, brand_essence: Dict = None, logo_color: str = None) -> Dict:
        """
        Generate comprehensive color system with primary colors, secondary colors, and usage guidelines
        
        Returns:
            Dict: {
                'primary_colors': [color_specs...],
                'secondary_colors': [color_specs...], 
                'usage_guidelines': str
            }
        """
        print(f"🎨 Researching color psychology for {company_name} in {industry} industry...")
        
        # Step 1: Research industry color trends and psychology
        color_research = self._research_industry_colors(company_name, industry, values)
        
        # Step 2: Generate primary colors (3-4 colors)
        primary_colors = self._generate_primary_colors(company_name, industry, values, audience, color_research, logo_color)
        
        # Step 3: Generate secondary colors (5 colors)
        secondary_colors = self._generate_secondary_colors(primary_colors, company_name, industry)
        
        # Step 4: Generate usage guidelines
        usage_guidelines = self._generate_color_usage_guidelines(primary_colors, secondary_colors, company_name, industry)
        
        return {
            'primary_colors': primary_colors,
            'secondary_colors': secondary_colors,
            'usage_guidelines': usage_guidelines
        }
    
    def _research_industry_colors(self, company_name: str, industry: str, values: str) -> Dict:
        """Research industry-specific color trends and psychology"""
        try:
            if self.serper_api_key:
                print("🌐 Conducting web research on industry color trends...")
                
                # Search for industry color trends
                search_query = f"{industry} industry color palette trends 2024 brand colors psychology"
                search_results = self._web_search(search_query)
                
                # Generate insights from research
                research_insights = self._analyze_color_research(search_results, industry, values)
                return research_insights
            else:
                print("⚠️ No Serper API key found, using industry knowledge base...")
                return self._get_industry_color_knowledge(industry)
                
        except Exception as e:
            print(f"❌ Color research failed: {e}")
            return self._get_industry_color_knowledge(industry)
    
    def _web_search(self, query: str) -> List[Dict]:
        """Perform web search for color research"""
        try:
            url = "https://google.serper.dev/search"
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            data = {
                'q': query,
                'num': 5
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json().get('organic', [])
            else:
                print(f"❌ Search API failed: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Web search failed: {e}")
            return []
    
    def _analyze_color_research(self, search_results: List[Dict], industry: str, values: str) -> Dict:
        """Analyze web research results to extract color insights"""
        try:
            # Combine search results
            research_text = ""
            for result in search_results[:3]:
                research_text += f"{result.get('title', '')} {result.get('snippet', '')} "
            
            if self.openai_api_key:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                
                prompt = f"""Analyze this color research for {industry} industry and extract key insights:

Research Text:
{research_text}

Company Values: {values}

Extract and provide:
1. 3 key color psychology insights for this industry
2. 3 trending color directions
3. Colors to avoid and why
4. Recommended color temperature (warm/cool/balanced)

Format as JSON with keys: insights, trends, avoid, temperature"""

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a color psychology expert analyzing industry trends."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400,
                    temperature=0.7
                )
                
                result = response.choices[0].message.content.strip()
                try:
                    return json.loads(result)
                except:
                    print("⚠️ Failed to parse AI color analysis, using fallback")
                    
        except Exception as e:
            print(f"❌ Color research analysis failed: {e}")
        
        return self._get_industry_color_knowledge(industry)
    
    def _get_industry_color_knowledge(self, industry: str) -> Dict:
        """Fallback industry color psychology knowledge base"""
        industry_colors = {
            'technology': {
                'insights': ['Blue conveys trust and reliability', 'Green suggests innovation and growth', 'Purple indicates creativity and forward-thinking'],
                'trends': ['Deep blues with tech accent colors', 'Gradient combinations', 'High contrast for accessibility'],
                'avoid': ['Overly bright or neon colors', 'Too many competing colors'],
                'temperature': 'cool'
            },
            'healthcare': {
                'insights': ['Blue builds trust and professionalism', 'Green represents health and healing', 'White suggests cleanliness and sterility'],
                'trends': ['Calming blues and greens', 'Clean, minimal palettes', 'Accessible color combinations'],
                'avoid': ['Red (associated with danger)', 'Very dark colors'],
                'temperature': 'cool'
            },
            'finance': {
                'insights': ['Blue conveys stability and trust', 'Green represents prosperity', 'Navy suggests authority and expertise'],
                'trends': ['Classic blue and gold combinations', 'Conservative, professional tones', 'Sophisticated gradients'],
                'avoid': ['Overly vibrant colors', 'Colors that suggest risk'],
                'temperature': 'cool'
            },
            'fintech': {
                'insights': ['Blue conveys stability and trust', 'Green represents growth and money', 'Purple suggests innovation'],
                'trends': ['Modern blues with green accents', 'Tech-forward gradients', 'Minimalist professional tones'],
                'avoid': ['Red (suggests risk)', 'Overly playful colors'],
                'temperature': 'cool'
            },
            'education': {
                'insights': ['Blue promotes learning and trust', 'Orange stimulates enthusiasm', 'Green encourages growth'],
                'trends': ['Bright, engaging colors', 'Accessible combinations', 'Youth-friendly palettes'],
                'avoid': ['Overly dark or serious colors', 'Low contrast combinations'],
                'temperature': 'balanced'
            },
            'retail': {
                'insights': ['Red creates urgency and excitement', 'Orange promotes enthusiasm', 'Purple suggests luxury'],
                'trends': ['Bold, attention-grabbing colors', 'Seasonal palette variations', 'Brand differentiation colors'],
                'avoid': ['Dull or muted colors', 'Colors that reduce visibility'],
                'temperature': 'warm'
            },
            'media': {
                'insights': ['Navy conveys authority and credibility', 'Red suggests urgency and breaking news', 'Black represents sophistication and premium content'],
                'trends': ['Classic navy and black combinations', 'High contrast for readability', 'Professional editorial colors'],
                'avoid': ['Overly bright colors that distract from content', 'Low contrast combinations'],
                'temperature': 'cool'
            },
            'publishing': {
                'insights': ['Navy builds trust and authority', 'Black suggests premium quality', 'Gray provides neutral balance'],
                'trends': ['Editorial navy and black schemes', 'Classic serif-friendly colors', 'High readability combinations'],
                'avoid': ['Colors that interfere with text readability', 'Overly trendy colors'],
                'temperature': 'cool'
            },
            'news': {
                'insights': ['Navy conveys credibility and trust', 'Red indicates urgency and importance', 'White ensures clean readability'],
                'trends': ['Traditional news colors (navy, red, white)', 'High contrast for accessibility', 'Professional editorial palette'],
                'avoid': ['Colors that suggest bias', 'Low contrast combinations'],
                'temperature': 'cool'
            },
            'consulting': {
                'insights': ['Blue builds trust and expertise', 'Gray suggests professionalism', 'Navy conveys authority'],
                'trends': ['Conservative professional tones', 'Sophisticated color combinations', 'Executive-level palettes'],
                'avoid': ['Overly creative or playful colors', 'Trendy colors that may date quickly'],
                'temperature': 'cool'
            },
            'creative': {
                'insights': ['Purple stimulates creativity', 'Orange promotes energy and enthusiasm', 'Teal suggests innovation'],
                'trends': ['Bold creative combinations', 'Gradient and vibrant accents', 'Artistic color schemes'],
                'avoid': ['Overly conservative colors', 'Monochromatic schemes'],
                'temperature': 'warm'
            },
            'nonprofit': {
                'insights': ['Blue builds trust and reliability', 'Green represents hope and growth', 'Warm colors show compassion'],
                'trends': ['Trustworthy blues with warm accents', 'Accessible color combinations', 'Hopeful and optimistic palettes'],
                'avoid': ['Luxury colors that suggest excess', 'Cold or unwelcoming combinations'],
                'temperature': 'balanced'
            },
            'ecommerce': {
                'insights': ['Blue builds trust for transactions', 'Green suggests security and go', 'Orange creates urgency for CTAs'],
                'trends': ['Trust-building primary colors', 'High conversion accent colors', 'Mobile-optimized palettes'],
                'avoid': ['Colors that reduce conversion', 'Low contrast for buttons'],
                'temperature': 'balanced'
            }
        }
        
        # Match industry or return generic
        for key in industry_colors:
            if key.lower() in industry.lower():
                return industry_colors[key]
        
        # Generic business colors
        return {
            'insights': ['Blue builds trust and professionalism', 'Green suggests growth and stability', 'Gray provides neutral balance'],
            'trends': ['Professional blue-based palettes', 'Subtle accent colors', 'High accessibility contrast'],
            'avoid': ['Overly bright or unprofessional colors'],
            'temperature': 'balanced'
        }
    
    def _generate_primary_colors(self, company_name: str, industry: str, values: str, 
                                audience: str, research: Dict, logo_color: str = None) -> List[Dict]:
        """Generate 3-4 primary colors with detailed specifications"""
        try:
            if self.openai_api_key:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                
                logo_color_instruction = ""
                if logo_color:
                    normalized_logo_color = self._normalize_color_input(logo_color)
                    if normalized_logo_color:
                        logo_color_instruction = f"\n- User's preferred logo color: {normalized_logo_color} (MUST be included as the first primary color)"
                
                prompt = f"""Generate 3-4 primary brand colors for {company_name} in {industry} industry.

Company Context:
- Values: {values}
- Target Audience: {audience}{logo_color_instruction}

Color Research Insights:
- Key insights: {', '.join(research.get('insights', []))}
- Trends: {', '.join(research.get('trends', []))}
- Temperature preference: {research.get('temperature', 'balanced')}

Requirements:
1. Generate 3-4 distinct primary colors
2. {'If a logo color is specified, use it as the first primary color' if logo_color else 'Each color should have a name (e.g., "Primary Blue", "Accent Green")'}
3. Each color should have a descriptive name
4. Provide HEX codes that work well together
5. Consider accessibility and contrast
6. Ensure colors align with industry psychology
7. Make colors distinctive and memorable

Return as JSON array:
[
  {{
    "name": "Primary Blue",
    "hex": "#2E86AB",
    "description": "Trust and reliability"
  }},
  ...
]"""

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional brand color designer creating primary color palettes."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                result = response.choices[0].message.content.strip()
                try:
                    colors_data = json.loads(result)
                    # Add detailed specifications to each color
                    detailed_colors = []
                    for color in colors_data:
                        detailed_color = self._add_color_specifications(color)
                        detailed_colors.append(detailed_color)
                    return detailed_colors
                except:
                    print("⚠️ Failed to parse AI primary colors, using fallback")
                    
        except Exception as e:
            print(f"❌ Primary color generation failed: {e}")
        
        return self._generate_fallback_primary_colors(industry, research, logo_color)
    
    def _generate_secondary_colors(self, primary_colors: List[Dict], company_name: str, industry: str) -> List[Dict]:
        """Generate 5 secondary/accent colors that complement the primary palette"""
        try:
            if self.openai_api_key:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                
                primary_hex_codes = [color['hex'] for color in primary_colors]
                
                prompt = f"""Generate 5 secondary/accent colors for {company_name} that complement these primary colors:
Primary Colors: {', '.join(primary_hex_codes)}

Requirements:
1. Generate 5 secondary colors that work harmoniously with the primary palette
2. Include lighter tints and darker shades
3. Add neutral colors (grays) if appropriate
4. Ensure good contrast for accessibility
5. Consider colors for backgrounds, text, and accents
6. Each color should have a descriptive name

Return as JSON array:
[
  {{
    "name": "Light Gray",
    "hex": "#F8F9FA", 
    "description": "Background and subtle accents"
  }},
  ...
]"""

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional color designer creating secondary color palettes."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400,
                    temperature=0.7
                )
                
                result = response.choices[0].message.content.strip()
                try:
                    colors_data = json.loads(result)
                    # Add detailed specifications to each color
                    detailed_colors = []
                    for color in colors_data:
                        detailed_color = self._add_color_specifications(color)
                        detailed_colors.append(detailed_color)
                    return detailed_colors
                except:
                    print("⚠️ Failed to parse AI secondary colors, using fallback")
                    
        except Exception as e:
            print(f"❌ Secondary color generation failed: {e}")
        
        return self._generate_fallback_secondary_colors(primary_colors)
    
    def _add_color_specifications(self, color: Dict) -> Dict:
        """Add RGB, CMYK, and accessibility specifications to a color"""
        hex_color = color['hex']
        
        # Convert HEX to RGB
        rgb = self._hex_to_rgb(hex_color)
        
        # Convert RGB to CMYK
        cmyk = self._rgb_to_cmyk(rgb)
        
        # Determine text color for accessibility
        text_color = self._get_accessible_text_color(rgb)
        
        return {
            'name': color['name'],
            'hex': hex_color,
            'rgb': f"RGB({rgb[0]}, {rgb[1]}, {rgb[2]})",
            'cmyk': f"CMYK({cmyk[0]}, {cmyk[1]}, {cmyk[2]}, {cmyk[3]})",
            'text_recommendation': text_color,
            'description': color.get('description', '')
        }
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert HEX color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_cmyk(self, rgb: Tuple[int, int, int]) -> Tuple[int, int, int, int]:
        """Convert RGB to CMYK"""
        r, g, b = [x/255.0 for x in rgb]
        
        k = 1 - max(r, g, b)
        if k == 1:
            return (0, 0, 0, 100)
        
        c = (1 - r - k) / (1 - k)
        m = (1 - g - k) / (1 - k)
        y = (1 - b - k) / (1 - k)
        
        return (int(c * 100), int(m * 100), int(y * 100), int(k * 100))
    
    def _get_accessible_text_color(self, rgb: Tuple[int, int, int]) -> str:
        """Determine if light or dark text should be used on this color"""
        # Calculate relative luminance
        def relative_luminance(color_value):
            normalized = color_value / 255.0
            if normalized <= 0.03928:
                return normalized / 12.92
            else:
                return pow((normalized + 0.055) / 1.055, 2.4)
        
        r_lum = relative_luminance(rgb[0])
        g_lum = relative_luminance(rgb[1])
        b_lum = relative_luminance(rgb[2])
        
        luminance = 0.2126 * r_lum + 0.7152 * g_lum + 0.0722 * b_lum
        
        # Return recommendation based on contrast ratio
        if luminance > 0.179:
            return "Use Dark Text"
        else:
            return "Use Light Text"
    
    def _generate_color_usage_guidelines(self, primary_colors: List[Dict], secondary_colors: List[Dict], 
                                       company_name: str, industry: str) -> str:
        """Generate comprehensive color usage guidelines"""
        try:
            if self.openai_api_key:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                
                primary_names = [color['name'] for color in primary_colors]
                secondary_names = [color['name'] for color in secondary_colors]
                
                prompt = f"""Create comprehensive color usage guidelines for {company_name} in the {industry} industry.

Primary Colors: {', '.join(primary_names)}
Secondary Colors: {', '.join(secondary_names)}

Create guidelines covering:
1. When to use each primary color
2. How to combine colors effectively
3. Digital vs print usage recommendations
4. Accessibility considerations
5. Do's and don'ts for color application

Write in a professional, clear style suitable for brand guidelines. Keep it comprehensive but concise."""

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a brand guidelines expert creating color usage documentation."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
                
        except Exception as e:
            print(f"❌ Color usage guidelines generation failed: {e}")
        
        return self._generate_fallback_usage_guidelines(company_name, industry)
    
    def _normalize_color_input(self, color_input):
        """Normalize various color input formats to hex"""
        if not color_input:
            return None
        
        color_input = color_input.strip()
        
        # If it's already a hex color
        if color_input.startswith('#') and len(color_input) == 7:
            return color_input
        
        # If it's hex without #
        if len(color_input) == 6 and all(c in '0123456789ABCDEFabcdef' for c in color_input):
            return '#' + color_input
        
        # If it's RGB format like "rgb(255, 255, 255)" or "255, 255, 255"
        import re
        rgb_match = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', color_input.lower())
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            return f"#{r:02x}{g:02x}{b:02x}"
        
        # If it's comma-separated RGB like "255, 255, 255"
        rgb_parts = [x.strip() for x in color_input.split(',')]
        if len(rgb_parts) == 3:
            try:
                r, g, b = map(int, rgb_parts)
                if all(0 <= x <= 255 for x in [r, g, b]):
                    return f"#{r:02x}{g:02x}{b:02x}"
            except ValueError:
                pass
        
        # Color name mapping
        color_names = {
            'red': '#DC2626', 'blue': '#2563EB', 'green': '#059669', 'yellow': '#F59E0B',
            'purple': '#7C3AED', 'orange': '#EA580C', 'pink': '#EC4899', 'teal': '#0891B2',
            'gray': '#6B7280', 'grey': '#6B7280', 'black': '#1F2937', 'white': '#FFFFFF',
            'navy': '#1E40AF', 'burgundy': '#7F1D1D', 'coral': '#FB7185', 'mint': '#6EE7B7',
            'sage': '#84CC16', 'gold': '#D97706', 'silver': '#9CA3AF', 'brown': '#92400E'
        }
        
        if color_input.lower() in color_names:
            return color_names[color_input.lower()]
        
        print(f"⚠️ Could not normalize color input '{color_input}', using default")
        return None
    
    def _generate_fallback_primary_colors(self, industry: str, research: Dict, logo_color: str = None) -> List[Dict]:
        """Generate fallback primary colors based on industry"""
        industry_palettes = {
            'technology': [
                {'name': 'Primary Blue', 'hex': '#2E86AB', 'description': 'Trust and reliability'},
                {'name': 'Accent Teal', 'hex': '#24A19C', 'description': 'Innovation and growth'},
                {'name': 'Deep Navy', 'hex': '#1B365D', 'description': 'Professionalism and depth'}
            ],
            'healthcare': [
                {'name': 'Medical Blue', 'hex': '#0077BE', 'description': 'Trust and care'},
                {'name': 'Healing Green', 'hex': '#00A86B', 'description': 'Health and vitality'},
                {'name': 'Soft Gray', 'hex': '#6B7280', 'description': 'Balance and calm'}
            ],
            'finance': [
                {'name': 'Corporate Blue', 'hex': '#1E40AF', 'description': 'Stability and trust'},
                {'name': 'Success Green', 'hex': '#059669', 'description': 'Growth and prosperity'},
                {'name': 'Premium Gold', 'hex': '#D97706', 'description': 'Value and excellence'}
            ],
            'fintech': [
                {'name': 'Fintech Blue', 'hex': '#1E40AF', 'description': 'Trust and stability'},
                {'name': 'Growth Green', 'hex': '#10B981', 'description': 'Financial growth'},
                {'name': 'Innovation Purple', 'hex': '#7C3AED', 'description': 'Tech innovation'}
            ],
            'media': [
                {'name': 'Editorial Navy', 'hex': '#1E3A8A', 'description': 'Authority and credibility'},
                {'name': 'Premium Black', 'hex': '#1F2937', 'description': 'Sophistication'},
                {'name': 'Accent Red', 'hex': '#DC2626', 'description': 'Urgency and importance'}
            ],
            'publishing': [
                {'name': 'Publisher Navy', 'hex': '#1E3A8A', 'description': 'Trust and authority'},
                {'name': 'Editorial Black', 'hex': '#111827', 'description': 'Premium quality'},
                {'name': 'Classic Gray', 'hex': '#4B5563', 'description': 'Neutral balance'}
            ],
            'news': [
                {'name': 'News Navy', 'hex': '#1E3A8A', 'description': 'Credibility and trust'},
                {'name': 'Breaking Red', 'hex': '#DC2626', 'description': 'Urgency and importance'},
                {'name': 'Clean White', 'hex': '#FFFFFF', 'description': 'Clean readability'}
            ],
            'consulting': [
                {'name': 'Executive Blue', 'hex': '#1E40AF', 'description': 'Trust and expertise'},
                {'name': 'Professional Gray', 'hex': '#4B5563', 'description': 'Sophistication'},
                {'name': 'Authority Navy', 'hex': '#1E3A8A', 'description': 'Leadership'}
            ],
            'creative': [
                {'name': 'Creative Purple', 'hex': '#7C3AED', 'description': 'Creativity and innovation'},
                {'name': 'Energy Orange', 'hex': '#EA580C', 'description': 'Enthusiasm and energy'},
                {'name': 'Innovation Teal', 'hex': '#0891B2', 'description': 'Fresh thinking'}
            ],
            'nonprofit': [
                {'name': 'Trust Blue', 'hex': '#2563EB', 'description': 'Reliability and trust'},
                {'name': 'Hope Green', 'hex': '#059669', 'description': 'Growth and hope'},
                {'name': 'Compassion Orange', 'hex': '#EA580C', 'description': 'Warmth and care'}
            ],
            'ecommerce': [
                {'name': 'Trust Blue', 'hex': '#2563EB', 'description': 'Transaction trust'},
                {'name': 'Action Green', 'hex': '#10B981', 'description': 'Security and go'},
                {'name': 'CTA Orange', 'hex': '#F59E0B', 'description': 'Urgency and action'}
            ]
        }
        
        # Find matching industry or use default
        for key in industry_palettes:
            if key.lower() in industry.lower():
                colors = industry_palettes[key].copy()  # Create a copy to avoid modifying original
                break
        else:
            colors = industry_palettes['technology'].copy()  # Default
        
        # If logo_color is provided, use it as the first primary color
        if logo_color:
            normalized_logo_color = self._normalize_color_input(logo_color)
            if normalized_logo_color:
                # Create logo color entry
                logo_color_entry = {
                    'name': 'Logo Primary', 
                    'hex': normalized_logo_color, 
                    'description': 'User-specified logo color'
                }
                # Insert at the beginning and limit to 4 colors total
                colors = [logo_color_entry] + colors[:3]
        
        # Add detailed specifications
        detailed_colors = []
        for color in colors:
            detailed_color = self._add_color_specifications(color)
            detailed_colors.append(detailed_color)
        
        return detailed_colors
    
    def _generate_fallback_secondary_colors(self, primary_colors: List[Dict]) -> List[Dict]:
        """Generate fallback secondary colors"""
        secondary_colors = [
            {'name': 'Light Background', 'hex': '#F8F9FA', 'description': 'Clean backgrounds'},
            {'name': 'Medium Gray', 'hex': '#6B7280', 'description': 'Text and borders'},
            {'name': 'Dark Text', 'hex': '#1F2937', 'description': 'Primary text color'},
            {'name': 'Accent Light', 'hex': '#E5E7EB', 'description': 'Subtle highlights'},
            {'name': 'Warning Orange', 'hex': '#F59E0B', 'description': 'Alerts and attention'}
        ]
        
        # Add detailed specifications
        detailed_colors = []
        for color in secondary_colors:
            detailed_color = self._add_color_specifications(color)
            detailed_colors.append(detailed_color)
        
        return detailed_colors
    
    def _generate_fallback_usage_guidelines(self, company_name: str, industry: str) -> str:
        """Generate fallback color usage guidelines"""
        return f"""Color Usage Guidelines for {company_name}

Primary Color Applications:
• Use primary colors for logos, headlines, and key brand elements
• Primary colors should dominate in brand communications
• Maintain consistent usage across all touchpoints

Color Combinations:
• Pair primary colors with neutral backgrounds for maximum impact
• Use secondary colors to support and enhance primary palette
• Ensure sufficient contrast for accessibility (4.5:1 minimum)

Digital Guidelines:
• RGB values for web and digital applications
• Test colors across different devices and screens
• Consider dark mode compatibility

Print Guidelines:
• Use CMYK values for professional printing
• Account for paper color and texture variations
• Test color reproduction before final printing

Accessibility:
• Follow recommended text color guidelines
• Ensure color is not the only way to convey information
• Test with colorblind accessibility tools

Do's:
✓ Maintain color consistency across all materials
✓ Use colors purposefully to support brand message
✓ Test accessibility in all applications

Don'ts:
✗ Don't alter brand colors without approval
✗ Avoid using colors that clash with the primary palette
✗ Don't sacrifice readability for aesthetic choices"""


# Example usage and testing
if __name__ == "__main__":
    agent = EnhancedColorResearchAgent()
    
    # Test data
    test_company = "TechForward Inc"
    test_industry = "Technology"
    test_values = "Innovation, Simplicity, Human-Centered"
    test_audience = "Progressive businesses seeking digital transformation"
    
    color_system = agent.generate_comprehensive_color_system(
        test_company, test_industry, test_values, test_audience
    )
    
    print("Generated Color System:")
    print(f"Primary Colors: {len(color_system['primary_colors'])} colors")
    print(f"Secondary Colors: {len(color_system['secondary_colors'])} colors")
    print(f"Usage Guidelines: {len(color_system['usage_guidelines'])} characters")