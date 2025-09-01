import os
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import fal_client as fal
from decouple import config
from tools.serper_search import search_google
from PIL import Image

class IconographyAgent:
    """
    Agent responsible for generating brand-consistent iconography through web research
    and AI icon generation using Fal AI.
    """
    
    def __init__(self):
        """Initialize the IconographyAgent with API configurations"""
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.fal_key = config('FAL_KEY')
        os.environ['FAL_KEY'] = self.fal_key
    
    def ensure_black_background(self, image_path: str):
        """
        Force pitch black background using PIL post-processing
        
        Args:
            image_path: Path to the generated icon image
        """
        try:
            img = Image.open(image_path).convert("RGBA")
            black_bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
            final = Image.alpha_composite(black_bg, img)
            final.convert("RGB").save(image_path)  # overwrite with black bg
            print(f"    ✅ Applied pitch black background to {os.path.basename(image_path)}")
        except Exception as e:
            print(f"    ⚠️ Failed to apply black background to {os.path.basename(image_path)}: {e}")
        
    def analyze_icon_styles(self, company_name: str, industry: str, values: str, 
                          audience: str) -> Dict:
        """
        Research relevant icon styles for the company through web search
        
        Args:
            company_name: Name of the company
            industry: Company's industry/sector  
            values: Company core values
            audience: Target audience description
            
        Returns:
            Dictionary with icon style analysis and recommendations
        """
        print(f"  🔍 Researching iconography styles for {company_name}...")
        
        # Prepare search queries for comprehensive icon research
        search_queries = [
            f"{industry} icon design trends 2024",
            f"{industry} brand iconography best practices",
            f"minimalist icons for {industry} companies",
            f"{industry} UI/UX icon styles"
        ]
        
        # Add value-based searches
        if values:
            value_list = [v.strip() for v in values.split(',')]
            for value in value_list[:2]:  # Limit to top 2 values
                search_queries.append(f"{value} icon symbolism design")
        
        all_research = []
        icon_recommendations = {
            "common_themes": [],
            "recommended_styles": [],
            "industry_patterns": [],
            "color_preferences": [],
            "symbolic_elements": []
        }
        
        for query in search_queries[:4]:  # Limit to 4 searches to manage API usage
            try:
                results = search_google(query, max_results=3)
                if results:
                    all_research.extend(results)
                    
                    # Analyze results for icon patterns
                    for result in results:
                        snippet = result.get('snippet', '').lower()
                        title = result.get('title', '').lower()
                        
                        # Extract common icon style themes
                        if 'minimalist' in snippet or 'minimal' in snippet:
                            icon_recommendations["recommended_styles"].append("minimalist")
                        if 'flat design' in snippet:
                            icon_recommendations["recommended_styles"].append("flat")
                        if 'outline' in snippet or 'linear' in snippet:
                            icon_recommendations["recommended_styles"].append("outline")
                        if 'geometric' in snippet:
                            icon_recommendations["recommended_styles"].append("geometric")
                            
                        # Industry-specific patterns
                        if industry.lower() in snippet:
                            icon_recommendations["industry_patterns"].append(result['title'])
                            
            except Exception as e:
                print(f"  ⚠️ Error researching '{query}': {e}")
                continue
        
        # Remove duplicates and prioritize
        icon_recommendations["recommended_styles"] = list(set(icon_recommendations["recommended_styles"]))
        
        # Determine icon categories based on industry and values
        icon_categories = self._determine_icon_categories(industry, values, audience)
        
        research_summary = {
            "research_data": all_research[:10],  # Keep top 10 results
            "icon_recommendations": icon_recommendations,
            "suggested_categories": icon_categories,
            "research_queries": search_queries,
            "total_sources": len(all_research)
        }
        
        print(f"  ✅ Analyzed {len(all_research)} sources for icon insights")
        return research_summary
    
    def _determine_icon_categories(self, industry: str, values: str, audience: str) -> List[str]:
        """
        Determine relevant icon categories based on company information
        
        Args:
            industry: Company's industry
            values: Company values
            audience: Target audience
            
        Returns:
            List of icon categories to generate
        """
        base_categories = ["innovation", "growth", "collaboration", "quality"]
        industry_categories = {
            "technology": ["code", "data", "network", "security", "innovation"],
            "healthcare": ["care", "health", "trust", "science", "support"],
            "finance": ["security", "growth", "trust", "stability", "investment"],
            "education": ["knowledge", "growth", "innovation", "community", "achievement"],
            "retail": ["customer", "service", "quality", "convenience", "experience"],
            "manufacturing": ["precision", "efficiency", "quality", "innovation", "reliability"],
            "consulting": ["expertise", "strategy", "growth", "analysis", "guidance"],
            "media": ["creativity", "communication", "innovation", "engagement", "storytelling"]
        }
        
        # Match industry to categories
        categories = base_categories.copy()
        industry_lower = industry.lower()
        
        for key, industry_icons in industry_categories.items():
            if key in industry_lower:
                categories.extend(industry_icons[:3])  # Add top 3 industry-specific icons
                break
        
        # Add value-based categories
        if values:
            value_list = [v.strip().lower() for v in values.split(',')]
            for value in value_list[:3]:  # Limit to top 3 values
                if value in ["innovation", "quality", "trust", "growth", "collaboration"]:
                    categories.append(value)
        
        # Remove duplicates and limit to 6 icons
        return list(set(categories))[:6]
    
    def generate_brand_icons(self, company_name: str, industry: str, values: str,
                           audience: str, primary_color_hex: str, 
                           research_data: Dict = None) -> Dict:
        """
        Generate brand-consistent icons using Fal AI based on research insights
        
        Args:
            company_name: Name of the company
            industry: Company's industry
            values: Company core values
            audience: Target audience
            primary_color_hex: Primary brand color in hex format
            research_data: Optional research data from analyze_icon_styles
            
        Returns:
            Dictionary with generated icon information
        """
        print(f"  🎨 Generating brand icons for {company_name}...")
        
        # Get icon categories to generate
        if research_data and research_data.get("suggested_categories"):
            icon_categories = research_data["suggested_categories"]
        else:
            icon_categories = self._determine_icon_categories(industry, values, audience)
        
        # Determine style based on research
        icon_style = "minimalist flat"
        if research_data and research_data.get("icon_recommendations"):
            styles = research_data["icon_recommendations"].get("recommended_styles", [])
            if styles:
                icon_style = " ".join(styles[:2])  # Use top 2 recommended styles
        
        generated_icons = []
        successful_generations = 0
        
        # Create output directory
        os.makedirs("output", exist_ok=True)
        
        for i, category in enumerate(icon_categories):
            try:
                # Create strengthened prompt with background emphasis first
                prompt = (
                    f"Flat {icon_style} icon, centered on a pure solid pitch black (#000000) background. "
                    f"Icon symbol in {primary_color_hex} only. "
                    f"Minimalist corporate branding style for {industry} industry. "
                    f"Simple, clean, professional, high-contrast. "
                    f"No gradients, no shadows, no glow, no lighting effects, no 3D. "
                    f"Strictly keep background pitch black (#000000). "
                    f"Representing '{category}' concept."
                )
                
                # Generate icon using Fal AI with expanded negative prompt
                result = fal.run(
                    "fal-ai/ideogram/v2a",
                    arguments={
                        "prompt": prompt,
                        "aspect_ratio": "1:1",  # Square format for icons
                        "style": "auto",
                        "negative_prompt": (
                            "white background, transparent background, blank background, "
                            "gradient background, colored background, textured background, "
                            "realistic lighting, glow, reflections, shadows, 3D effects, "
                            "complex details, realistic textures"
                        )
                    }
                )
                
                image_url = result['images'][0]['url']
                
                # Download and save the icon
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"{company_name.lower().replace(' ', '_')}_icon_{category}_{timestamp}_{unique_id}.png"
                    local_path = os.path.join("output", filename)
                    
                    with open(local_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    # Force pitch black background using post-processing
                    self.ensure_black_background(local_path)
                    
                    icon_info = {
                        "category": category,
                        "icon_number": i + 1,
                        "image_url": image_url,
                        "local_path": local_path,
                        "filename": filename,
                        "prompt": prompt,
                        "style": icon_style,
                        "color": primary_color_hex,
                        "seed": result.get('seed')
                    }
                    
                    generated_icons.append(icon_info)
                    successful_generations += 1
                    print(f"  ✅ Generated icon for '{category}': {local_path}")
                    
                else:
                    error_info = {
                        "category": category,
                        "icon_number": i + 1,
                        "error": f"Failed to download icon: {image_response.status_code}",
                        "local_path": "Failed to download"
                    }
                    generated_icons.append(error_info)
                    print(f"  ❌ Failed to download icon for '{category}'")
                    
            except Exception as e:
                error_info = {
                    "category": category,
                    "icon_number": i + 1,
                    "error": f"Error generating icon: {str(e)}",
                    "local_path": "Error"
                }
                generated_icons.append(error_info)
                print(f"  ❌ Error generating icon for '{category}': {str(e)}")
        
        # Return comprehensive results
        result_summary = {
            "generated_icons": generated_icons,
            "total_requested": len(icon_categories),
            "successful_generations": successful_generations,
            "company_name": company_name,
            "industry": industry,
            "primary_color": primary_color_hex,
            "icon_style": icon_style,
            "categories": icon_categories,
            "research_based": research_data is not None
        }
        
        print(f"  🎯 Generated {successful_generations}/{len(icon_categories)} icons successfully")
        return result_summary
    
    def create_iconography_system(self, company_name: str, industry: str, values: str,
                                audience: str, primary_color_hex: str) -> Dict:
        """
        Complete iconography creation workflow: research + generation
        
        Args:
            company_name: Name of the company
            industry: Company's industry
            values: Company core values
            audience: Target audience
            primary_color_hex: Primary brand color in hex format
            
        Returns:
            Complete iconography system data
        """
        print(f"  🎨 Creating complete iconography system for {company_name}...")
        
        # Step 1: Research icon styles and trends
        research_data = self.analyze_icon_styles(company_name, industry, values, audience)
        
        # Step 2: Generate brand icons based on research
        icon_generation_results = self.generate_brand_icons(
            company_name, industry, values, audience, 
            primary_color_hex, research_data
        )
        
        # Step 3: Compile complete system
        iconography_system = {
            "company_name": company_name,
            "research_analysis": research_data,
            "icon_generation": icon_generation_results,
            "system_overview": {
                "total_icons": icon_generation_results["successful_generations"],
                "style_approach": icon_generation_results["icon_style"],
                "color_system": primary_color_hex,
                "background_standard": "#000000",
                "industry_context": industry,
                "research_informed": True
            },
            "usage_guidelines": {
                "minimum_size": "16px for web, 0.5 inches for print",
                "spacing": "Minimum clear space of 50% icon width around each icon",
                "color_usage": f"Primary: {primary_color_hex}, Background: #000000 only",
                "applications": ["Digital interfaces", "Print materials", "Presentations", "Marketing collateral"]
            }
        }
        
        print(f"  ✅ Iconography system complete with {iconography_system['system_overview']['total_icons']} icons")
        return iconography_system

# Example usage and testing
if __name__ == "__main__":
    # Test the IconographyAgent
    agent = IconographyAgent()
    
    # Test with sample data
    result = agent.create_iconography_system(
        company_name="TechForward",
        industry="Technology",
        values="Innovation, Quality, Trust",
        audience="Tech professionals and enterprises",
        primary_color_hex="#2E86AB"
    )
    
    print("\n" + "="*50)
    print("Iconography System Generated:")
    print(json.dumps(result, indent=2))