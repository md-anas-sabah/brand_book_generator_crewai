import os
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
import uuid
from tools.serper_search import search_google
from PIL import Image

class IconographyAgent:
    """
    Agent responsible for generating brand-consistent iconography through web research
    and Iconify API for professional SVG icons.
    """
    
    def __init__(self):
        """Initialize the IconographyAgent with API configurations"""
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        
        # Industry-specific icon mappings - realistic app icons
        self.icon_mappings = {
            "technology": {
                "core": ["mdi:home", "mdi:cog", "mdi:account", "mdi:code-tags", "mdi:database", 
                        "mdi:server", "mdi:cloud", "mdi:security", "mdi:api", "mdi:bug",
                        "mdi:console", "mdi:monitor", "mdi:keyboard", "mdi:mouse", "mdi:chip"],
                "industry": ["mdi:github", "mdi:gitlab", "mdi:docker", "mdi:kubernetes", "mdi:aws",
                           "mdi:google-cloud", "mdi:microsoft-azure", "mdi:slack", "mdi:discord", "mdi:telegram",
                           "mdi:linkedin", "mdi:stack-overflow", "mdi:reddit", "mdi:twitter", "mdi:youtube"]
            },
            "business": {
                "core": ["mdi:home", "mdi:account", "mdi:cog", "mdi:briefcase", "mdi:office-building",
                        "mdi:handshake", "mdi:chart-line", "mdi:presentation", "mdi:calendar", "mdi:email",
                        "mdi:phone", "mdi:message", "mdi:file-document", "mdi:folder", "mdi:printer"],
                "industry": ["mdi:linkedin", "mdi:microsoft", "mdi:google", "mdi:zoom", "mdi:teams",
                           "mdi:slack", "mdi:dropbox", "mdi:onedrive", "mdi:facebook", "mdi:twitter",
                           "mdi:instagram", "mdi:whatsapp", "mdi:telegram", "mdi:skype", "mdi:email"]
            },
            "healthcare": {
                "core": ["mdi:home", "mdi:account", "mdi:cog", "mdi:hospital-box", "mdi:heart",
                        "mdi:medical-bag", "mdi:pill", "mdi:stethoscope", "mdi:calendar", "mdi:phone",
                        "mdi:email", "mdi:bell", "mdi:clipboard-pulse", "mdi:thermometer", "mdi:bandage"],
                "industry": ["mdi:doctor", "mdi:ambulance", "mdi:wheelchair", "mdi:dna", "mdi:microscope",
                           "mdi:test-tube", "mdi:tooth", "mdi:eye", "mdi:brain", "mdi:baby",
                           "mdi:meditation", "mdi:yoga", "mdi:leaf", "mdi:water", "mdi:run"]
            },
            "education": {
                "core": ["mdi:home", "mdi:account", "mdi:cog", "mdi:school", "mdi:book-open",
                        "mdi:graduation-cap", "mdi:library", "mdi:pencil", "mdi:calculator", "mdi:calendar",
                        "mdi:email", "mdi:bell", "mdi:certificate", "mdi:trophy-award", "mdi:notebook"],
                "industry": ["mdi:blackboard", "mdi:teach", "mdi:backpack", "mdi:science-beaker", "mdi:atom",
                           "mdi:telescope", "mdi:earth", "mdi:music-note", "mdi:palette", "mdi:theater",
                           "mdi:basketball", "mdi:piano", "mdi:camera-retro", "mdi:video", "mdi:puzzle"]
            },
            "retail": {
                "core": ["mdi:home", "mdi:account", "mdi:cog", "mdi:shopping", "mdi:cart",
                        "mdi:store", "mdi:tag", "mdi:currency-usd", "mdi:gift", "mdi:package",
                        "mdi:truck", "mdi:star", "mdi:heart", "mdi:phone", "mdi:email"],
                "industry": ["mdi:tshirt-crew", "mdi:shoe-heel", "mdi:watch", "mdi:sunglasses", "mdi:food",
                           "mdi:coffee", "mdi:cake", "mdi:flower", "mdi:book", "mdi:toy-brick",
                           "mdi:gamepad", "mdi:music", "mdi:movie", "mdi:share", "mdi:thumbs-up"]
            },
            "finance": {
                "core": ["mdi:home", "mdi:account", "mdi:cog", "mdi:bank", "mdi:cash",
                        "mdi:credit-card", "mdi:chart-line", "mdi:calculator", "mdi:security", "mdi:shield-check",
                        "mdi:lock", "mdi:trending-up", "mdi:phone", "mdi:email", "mdi:bell"],
                "industry": ["mdi:bitcoin", "mdi:currency-eth", "mdi:piggy-bank", "mdi:wallet", "mdi:receipt",
                           "mdi:file-document", "mdi:signature", "mdi:percent", "mdi:arrow-up-bold", "mdi:arrow-down-bold",
                           "mdi:swap-horizontal", "mdi:safe", "mdi:scale-balance", "mdi:handshake", "mdi:timer"]
            }
        }
    
    def get_iconify_icon(self, icon_name: str, logo_color: str = None, size: int = 64) -> str:
        """
        Download SVG icon from Iconify API and apply logo color
        
        Args:
            icon_name: Icon name (e.g., "mdi:home")
            logo_color: Logo color to apply to icon (e.g., "#FF5733")
            size: Icon size in pixels
            
        Returns:
            Path to saved colored SVG file
        """
        try:
            # Create output directory
            os.makedirs("output/icons", exist_ok=True)
            
            # Download SVG from Iconify API
            url = f"https://api.iconify.design/{icon_name}.svg"
            params = {"height": size, "width": size}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Failed to download icon {icon_name}: {response.status_code}")
                return None
            
            svg_content = response.text
            
            # Apply logo color if provided
            if logo_color:
                svg_content = self._apply_color_to_svg(svg_content, logo_color)
            
            # Save colored SVG
            icon_filename = f"{icon_name.replace(':', '_')}_{logo_color[1:] if logo_color else 'default'}.svg"
            icon_path = os.path.join("output/icons", icon_filename)
            
            with open(icon_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            
            return icon_path
            
        except Exception as e:
            print(f"❌ Error getting Iconify icon {icon_name}: {e}")
            return None
    
    def _apply_color_to_svg(self, svg_content: str, color: str) -> str:
        """
        Apply color to SVG content
        
        Args:
            svg_content: Original SVG content
            color: Color to apply (hex format)
            
        Returns:
            Modified SVG content with applied color
        """
        # Method 1: Replace existing fill colors
        import re
        
        # Replace common fill attributes
        svg_content = re.sub(r'fill="[^"]*"', f'fill="{color}"', svg_content)
        svg_content = re.sub(r"fill='[^']*'", f'fill="{color}"', svg_content)
        
        # Method 2: Add fill to SVG root if no fill found
        if 'fill=' not in svg_content:
            svg_content = svg_content.replace('<svg', f'<svg fill="{color}"')
        
        # Replace currentColor references
        svg_content = svg_content.replace('currentColor', color)
        svg_content = svg_content.replace('#000', color)
        svg_content = svg_content.replace('#000000', color)
        
        return svg_content
    
    def get_industry_icons(self, industry: str, category: str = "core", count: int = 15, 
                          company_values: str = "", audience: str = "") -> List[str]:
        """
        Get industry-specific icon names with value-based customization
        
        Args:
            industry: Industry name
            category: "core" or "industry" 
            count: Number of icons to return
            company_values: Company values to influence icon selection
            audience: Target audience to influence icon selection
            
        Returns:
            List of icon names
        """
        industry_lower = industry.lower()
        values_lower = company_values.lower() if company_values else ""
        audience_lower = audience.lower() if audience else ""
        
        # Find matching industry
        base_icons = []
        for key in self.icon_mappings:
            if key in industry_lower or industry_lower in key:
                base_icons = self.icon_mappings[key].get(category, [])
                break
        
        # Fallback to business icons
        if not base_icons:
            base_icons = self.icon_mappings["business"][category]
        
        # Customize icons based on company values and audience
        customized_icons = self._customize_icons_by_values(base_icons, values_lower, audience_lower)
        
        return customized_icons[:count]
    
    def _customize_icons_by_values(self, base_icons: List[str], values: str, audience: str) -> List[str]:
        """Customize icon selection based on company values and audience"""
        icons = base_icons.copy()
        
        # Value-based icon additions/replacements
        value_mappings = {
            "family": ["mdi:home-heart", "mdi:baby", "mdi:family"],
            "innovation": ["mdi:lightbulb", "mdi:rocket", "mdi:creation"],
            "trust": ["mdi:shield-check", "mdi:handshake", "mdi:verification"],
            "sustainability": ["mdi:leaf", "mdi:recycle", "mdi:earth"],
            "community": ["mdi:account-group", "mdi:hands-helping", "mdi:heart"],
            "quality": ["mdi:star", "mdi:medal", "mdi:check-circle"],
            "security": ["mdi:lock", "mdi:shield", "mdi:security"],
            "creativity": ["mdi:palette", "mdi:brush", "mdi:creation"],
            "education": ["mdi:school", "mdi:book-open", "mdi:graduation-cap"],
            "health": ["mdi:heart", "mdi:medical-bag", "mdi:fitness"]
        }
        
        # Audience-based icon additions
        audience_mappings = {
            "young": ["mdi:gamepad", "mdi:music", "mdi:camera"],
            "professional": ["mdi:briefcase", "mdi:presentation", "mdi:chart-line"],
            "family": ["mdi:home-heart", "mdi:baby", "mdi:family"],
            "senior": ["mdi:accessibility", "mdi:heart", "mdi:phone"],
            "student": ["mdi:school", "mdi:book", "mdi:pencil"],
            "enterprise": ["mdi:office-building", "mdi:handshake", "mdi:security"]
        }
        
        # Add relevant icons based on values (replace last few icons)
        additions = []
        for value_key, value_icons in value_mappings.items():
            if value_key in values:
                additions.extend(value_icons[:2])  # Add top 2 relevant icons
        
        # Add relevant icons based on audience
        for audience_key, audience_icons in audience_mappings.items():
            if audience_key in audience:
                additions.extend(audience_icons[:1])  # Add top 1 relevant icon
        
        # Replace some base icons with value/audience-specific ones
        if additions:
            # Keep first 10 base icons, replace last 5 with additions
            icons = icons[:10] + additions[:5]
        
        return icons
    
    def create_transparent_background(self, image_path: str):
        """
        Convert any background to transparent using AI background removal.
        Optimized for preserving HD quality of icons.
        
        Args:
            image_path: Path to the generated icon image
        """
        try:
            # Method 1: Try AI-powered background removal with rembg (best quality)
            try:
                from rembg import remove
                
                # Open original image to get dimensions
                original_img = Image.open(image_path)
                original_size = original_img.size
                
                with open(image_path, 'rb') as input_file:
                    input_data = input_file.read()
                
                output_data = remove(input_data)
                
                # Create transparent version filename
                transparent_path = image_path.replace('.png', '_transparent.png')
                with open(transparent_path, 'wb') as output_file:
                    output_file.write(output_data)
                
                # Verify size is preserved
                transparent_img = Image.open(transparent_path)
                if transparent_img.size != original_size:
                    # Resize back to original if needed
                    transparent_img = transparent_img.resize(original_size, Image.Resampling.LANCZOS)
                    transparent_img.save(transparent_path, "PNG")
                
                print(f"    ✅ Created HD AI-removed background: {os.path.basename(transparent_path)}")
                return transparent_path
                
            except ImportError:
                print("    ⚠️ rembg not installed, using original with white background...")
                return None
                
            except Exception as e:
                print(f"    ⚠️ AI background removal failed: {e}, using original...")
                return None
            
        except Exception as e:
            print(f"    ⚠️ Failed to create transparent version: {e}")
            return None
        
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
                           research_data: Dict = None, custom_categories: list = None) -> Dict:
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
        if custom_categories:
            icon_categories = custom_categories
        elif research_data and research_data.get("suggested_categories"):
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
                # Create simple flat icon prompt
                prompt = (
                    f"Simple flat icon representing '{category}' concept, {industry} industry style. "
                    f"Ultra-flat 2D design, solid colors only, no gradients, no shadows, no 3D effects. "
                    f"Icon symbol in {primary_color_hex} color on pure white background (#FFFFFF). "
                    f"Minimalist, clean geometric shapes, sharp edges, vector style. "
                    f"Corporate icon set style, simple and professional, easy to recognize. "
                    f"Flat design only, no depth, no lighting, no textures, scalable vector quality."
                )
                
                # Generate HD icon using Fal AI Turbo with white/transparent background
                result = fal.run(
                    "fal-ai/ideogram/v2a/turbo",
                    arguments={
                        "prompt": prompt,
                        "aspect_ratio": "1:1",  # Square format for icons
                        "expand_prompt": True,
                        "style": "auto",
                        "negative_prompt": (
                            "black background, dark background, colored background, "
                            "gradient background, textured background, pattern background, "
                            "realistic lighting, glow, reflections, shadows, 3D effects, "
                            "complex details, realistic textures, low quality, blurry, transparent background"
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
                    
                    # Convert background to transparent
                    transparent_path = self.create_transparent_background(local_path)
                    if transparent_path:
                        # Update local_path to transparent version for better usability
                        final_path = transparent_path
                        final_filename = os.path.basename(transparent_path)
                    else:
                        final_path = local_path
                        final_filename = filename
                    
                    icon_info = {
                        "category": category,
                        "icon_number": i + 1,
                        "image_url": image_url,
                        "local_path": final_path,
                        "filename": final_filename,
                        "prompt": prompt,
                        "style": icon_style,
                        "color": primary_color_hex,
                        "seed": result.get('seed')
                    }
                    
                    generated_icons.append(icon_info)
                    successful_generations += 1
                    print(f"  ✅ Generated icon for '{category}': {final_path}")
                    
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
                                audience: str, primary_color_hex: str, custom_categories: list = None, icon_type: str = "both") -> Dict:
        """
        Complete iconography creation workflow using Iconify API
        
        Args:
            company_name: Name of the company
            industry: Company's industry
            values: Company core values
            audience: Target audience
            primary_color_hex: Primary brand color in hex format (logo color)
            
        Returns:
            Complete iconography system with 30 colored SVG icons
        """
        print(f"  🎨 Creating Iconify-based iconography system for {company_name}...")
        
        # Get icons based on requested type
        if icon_type == "core":
            # Only core icons for first slide
            core_icon_names = self.get_industry_icons(industry, "core", 15, values, audience)
            
            print(f"  📥 Downloading and coloring 15 core icons with {primary_color_hex}...")
            core_icons = []
            for icon_name in core_icon_names:
                icon_path = self.get_iconify_icon(icon_name, primary_color_hex, size=128)
                if icon_path:
                    core_icons.append({
                        "name": icon_name.replace("mdi:", "").replace("-", " ").title(),
                        "path": icon_path,
                        "icon_id": icon_name,
                        "color": primary_color_hex
                    })
            
            return {
                "core_icons": core_icons,
                "industry_icons": [],
                "total_icons": len(core_icons),
                "color_applied": primary_color_hex,
                "source": "Iconify API",
                "industry": industry,
                "icon_generation": {
                    "generated_icons": core_icons,
                    "style_notes": f"Core app icons from Iconify, colored with brand color {primary_color_hex}"
                }
            }
            
        elif icon_type == "industry":
            # Only industry icons for second slide
            industry_icon_names = self.get_industry_icons(industry, "industry", 15, values, audience)
            
            print(f"  📥 Downloading and coloring 15 industry-specific icons with {primary_color_hex}...")
            industry_icons = []
            for icon_name in industry_icon_names:
                icon_path = self.get_iconify_icon(icon_name, primary_color_hex, size=128)
                if icon_path:
                    industry_icons.append({
                        "name": icon_name.replace("mdi:", "").replace("-", " ").title(),
                        "path": icon_path,
                        "icon_id": icon_name,
                        "color": primary_color_hex
                    })
            
            return {
                "core_icons": [],
                "industry_icons": industry_icons,
                "total_icons": len(industry_icons),
                "color_applied": primary_color_hex,
                "source": "Iconify API",
                "industry": industry,
                "icon_generation": {
                    "generated_icons": industry_icons,
                    "style_notes": f"Industry-specific icons from Iconify, colored with brand color {primary_color_hex}"
                }
            }
            
        else:
            # Both types (legacy support)
            core_icon_names = self.get_industry_icons(industry, "core", 15, values, audience)
            industry_icon_names = self.get_industry_icons(industry, "industry", 15, values, audience)
            
            core_icons = []
            industry_icons = []
            
            print(f"  📥 Downloading and coloring 15 core icons with {primary_color_hex}...")
            for icon_name in core_icon_names:
                icon_path = self.get_iconify_icon(icon_name, primary_color_hex, size=128)
                if icon_path:
                    core_icons.append({
                        "name": icon_name.replace("mdi:", "").replace("-", " ").title(),
                        "path": icon_path,
                        "icon_id": icon_name,
                        "color": primary_color_hex
                    })
            
            print(f"  📥 Downloading and coloring 15 industry-specific icons with {primary_color_hex}...")
            for icon_name in industry_icon_names:
                icon_path = self.get_iconify_icon(icon_name, primary_color_hex, size=128)
                if icon_path:
                    industry_icons.append({
                        "name": icon_name.replace("mdi:", "").replace("-", " ").title(),
                        "path": icon_path,
                        "icon_id": icon_name,
                        "color": primary_color_hex
                    })
            
            return {
                "core_icons": core_icons,
                "industry_icons": industry_icons,
                "total_icons": len(core_icons) + len(industry_icons),
                "color_applied": primary_color_hex,
                "source": "Iconify API",
                "industry": industry,
                "icon_generation": {
                    "generated_icons": core_icons + industry_icons,
                    "style_notes": f"Professional SVG icons from Iconify, colored with brand color {primary_color_hex}"
                }
            }

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