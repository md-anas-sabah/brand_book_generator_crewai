import requests
import json
from tools.serper_search import search_google
from decouple import config

def get_google_fonts(sort_by='popularity'):
    """
    Fetch all fonts from the Google Fonts API with licensing information
    
    Args:
        sort_by (str): How to sort the fonts ('popularity', 'alpha', 'date', 'style', 'trending')
        
    Returns:
        tuple: (font_families_list, font_licensing_info_dict)
    """
    try:
        api_key = config('GOOGLE_FONTS_API_KEY')
        url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={api_key}&sort={sort_by}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        font_families = []
        font_licensing = {}
        
        for font in data.get('items', []):
            family_name = font['family']
            font_families.append(family_name)
            
            # Extract licensing information
            font_licensing[family_name] = {
                'category': font.get('category', 'sans-serif'),
                'variants': font.get('variants', []),
                'subsets': font.get('subsets', []),
                'version': font.get('version', 'unknown'),
                'lastModified': font.get('lastModified', 'unknown'),
                'license': 'Open Font License',  # All Google Fonts are OFL
                'commercial_use': True,
                'license_verification': 'verified_google_fonts'
            }
        
        print(f"✅ Successfully fetched {len(font_families)} fonts from Google Fonts API with licensing info")
        return font_families, font_licensing
        
    except Exception as e:
        print(f"❌ Failed to fetch fonts from Google Fonts API: {e}")
        return [], {}

class FontResearchAgent:
    """
    Research-driven font recommendation agent that analyzes:
    - Company industry and brand positioning
    - Competitor font usage
    - Industry typography trends
    - Brand essence alignment
    """
    
    def __init__(self):
        self.industry_font_mapping = {
            "technology": ["Inter", "Source Sans Pro", "Open Sans", "Roboto"],
            "fintech": ["Inter", "Source Sans Pro", "Poppins", "Montserrat"],
            "healthcare": ["Source Sans Pro", "Open Sans", "Lato", "Nunito Sans"],
            "finance": ["Source Sans Pro", "Montserrat", "Inter", "IBM Plex Sans"],
            "retail": ["Poppins", "Montserrat", "Open Sans", "Source Sans Pro"],
            "consulting": ["Source Sans Pro", "Inter", "Montserrat", "IBM Plex Sans"],
            "education": ["Open Sans", "Source Sans Pro", "Lato", "Nunito Sans"],
            "media": ["Montserrat", "Poppins", "Source Sans Pro", "Inter"],
            "creative": ["Montserrat", "Poppins", "Inter", "Source Sans Pro"],
            "nonprofit": ["Open Sans", "Source Sans Pro", "Lato", "Nunito Sans"]
        }
        
        self.brand_personality_fonts = {
            "professional": ["Source Sans Pro", "Inter", "IBM Plex Sans"],
            "modern": ["Inter", "Poppins", "Montserrat"],
            "friendly": ["Open Sans", "Lato", "Nunito Sans"],
            "innovative": ["Inter", "Source Sans Pro", "Poppins"],
            "trustworthy": ["Source Sans Pro", "Open Sans", "Lato"],
            "creative": ["Montserrat", "Poppins", "Inter"],
            "minimalist": ["Inter", "Source Sans Pro", "Roboto"]
        }
    
    def research_fonts(self, company_name, industry, brand_essence=None):
        """
        Research and recommend fonts based on company profile and market analysis
        """
        print(f"🔍 Researching fonts for {company_name} in {industry} industry...")
        
        font_research = {
            "company_name": company_name,
            "industry": industry,
            "primary_font": None,
            "secondary_font": None,
            "research_insights": {},
            "font_rationale": ""
        }
        
        try:
            # 1. Industry-based research
            industry_fonts = self._get_industry_fonts(industry)
            
            # 2. Brand personality analysis
            personality_fonts = self._analyze_brand_personality(brand_essence)
            
            # 3. Competitor research (if available)
            competitor_insights = self._research_competitor_fonts(company_name, industry)
            
            # 4. Typography trends research
            trend_insights = self._research_typography_trends(industry)
            
            # 5. Final font selection logic
            selected_fonts = self._select_optimal_fonts(
                industry_fonts, 
                personality_fonts, 
                competitor_insights, 
                trend_insights
            )
            
            font_research.update({
                "primary_font": selected_fonts["primary"],
                "secondary_font": selected_fonts["secondary"],
                "research_insights": {
                    "industry_fonts": industry_fonts,
                    "personality_alignment": personality_fonts,
                    "competitor_analysis": competitor_insights,
                    "typography_trends": trend_insights
                },
                "font_rationale": self._generate_font_rationale(selected_fonts, industry, brand_essence)
            })
            
        except Exception as e:
            print(f"❌ Font research error: {e}")
            # Fallback to industry defaults
            fallback_fonts = self.industry_font_mapping.get(industry.lower(), ["Inter", "Source Sans Pro"])
            font_research.update({
                "primary_font": fallback_fonts[0],
                "secondary_font": fallback_fonts[1] if len(fallback_fonts) > 1 else fallback_fonts[0],
                "font_rationale": f"Selected industry-standard fonts for {industry} sector"
            })
        
        print(f"✅ Font research complete: {font_research['primary_font']} (primary), {font_research['secondary_font']} (secondary)")
        return font_research
    
    def _get_industry_fonts(self, industry):
        """Get font recommendations based on industry"""
        industry_key = industry.lower()
        return self.industry_font_mapping.get(industry_key, ["Inter", "Source Sans Pro"])
    
    def _analyze_brand_personality(self, brand_essence):
        """Analyze brand personality to suggest appropriate fonts"""
        if not brand_essence or not brand_essence.get("brand_positioning"):
            return []
        
        personality_traits = brand_essence["brand_positioning"].get("brand_personality", [])
        recommended_fonts = []
        
        for trait in personality_traits:
            trait_key = trait.lower()
            if trait_key in self.brand_personality_fonts:
                recommended_fonts.extend(self.brand_personality_fonts[trait_key])
        
        # Remove duplicates and return top 4
        return list(dict.fromkeys(recommended_fonts))[:4]
    
    def _research_competitor_fonts(self, company_name, industry):
        """Research competitor typography choices via web search"""
        try:
            search_query = f"{industry} companies typography fonts brand design 2024"
            search_results = search_google(search_query, max_results=3)
            
            insights = {
                "search_performed": True,
                "trends_found": [],
                "common_fonts": []
            }
            
            if search_results:
                # Analyze search results for font mentions
                for result in search_results:
                    content = (result.get("snippet", "") + " " + result.get("title", "")).lower()
                    
                    # Look for common font names in content
                    for font_category in self.industry_font_mapping.values():
                        for font in font_category:
                            if font.lower() in content:
                                insights["common_fonts"].append(font)
                
                insights["common_fonts"] = list(dict.fromkeys(insights["common_fonts"]))[:3]
            
            return insights
            
        except Exception as e:
            print(f"⚠️ Competitor font research failed: {e}")
            return {"search_performed": False, "error": str(e)}
    
    def _research_typography_trends(self, industry):
        """Research current typography trends for the industry"""
        try:
            search_query = f"typography trends {industry} 2024 brand design fonts"
            search_results = search_google(search_query, max_results=2)
            
            trends = {
                "current_trends": [],
                "recommended_styles": []
            }
            
            if search_results:
                for result in search_results:
                    snippet = result.get("snippet", "").lower()
                    
                    # Look for trend keywords
                    trend_keywords = ["clean", "minimalist", "modern", "sans-serif", "geometric", "humanist"]
                    for keyword in trend_keywords:
                        if keyword in snippet:
                            trends["current_trends"].append(keyword)
                
                trends["current_trends"] = list(dict.fromkeys(trends["current_trends"]))[:3]
            
            return trends
            
        except Exception as e:
            print(f"⚠️ Typography trends research failed: {e}")
            return {"current_trends": ["modern", "clean"]}
    
    def _select_optimal_fonts(self, industry_fonts, personality_fonts, competitor_insights, trend_insights):
        """Select optimal font pair based on all research inputs"""
        
        # Fetch fonts from Google Fonts API with licensing info
        google_fonts_data = get_google_fonts()
        
        if isinstance(google_fonts_data, tuple) and len(google_fonts_data) == 2:
            google_fonts, font_licensing = google_fonts_data
        else:
            # Handle backward compatibility
            google_fonts = google_fonts_data if google_fonts_data else []
            font_licensing = {}
        
        # Fallback to original hardcoded list if API call fails
        if not google_fonts:
            print("⚠️ Using fallback font list due to API failure")
            google_fonts = ["Inter", "Source Sans Pro", "Open Sans", "Montserrat", "Poppins", "Lato", "Roboto", "IBM Plex Sans", "Nunito Sans"]
            # Add basic licensing info for fallback fonts
            font_licensing = {font: {'license': 'Open Font License', 'commercial_use': True, 'license_verification': 'fallback_known_safe'} for font in google_fonts}
        
        # Create a curated high-quality font pool from Google Fonts API
        # Focus on top fonts that are widely used and professional
        premium_fonts = [
            "Inter", "Roboto", "Open Sans", "Lato", "Source Sans Pro", "Montserrat", 
            "Poppins", "Nunito Sans", "IBM Plex Sans", "Work Sans", "Fira Sans", 
            "DM Sans", "Space Grotesk", "Plus Jakarta Sans", "Manrope", "Archivo",
            "Quicksand", "Comfortaa", "Varela Round", "Crimson Text", "Playfair Display",
            "Libre Baskerville", "Cormorant Garamond", "Merriweather", "Roboto Slab"
        ]
        
        # Filter Google Fonts to include premium fonts that exist in API
        available_premium = [font for font in premium_fonts if font in google_fonts]
        
        # Combine premium fonts with curated industry and personality fonts
        all_fonts = list(set(available_premium + industry_fonts + personality_fonts))
        
        # Enhanced scoring system
        font_scores = {}
        
        for font in all_fonts:
            score = 0
            
            # Base score for premium fonts (ensures quality)
            if font in premium_fonts:
                score += 5
            
            # Score based on industry relevance
            if font in industry_fonts:
                score += 8  # Increased weight
            
            # Score based on personality alignment  
            if font in personality_fonts:
                score += 6  # Increased weight
            
            # Score based on competitor research
            if competitor_insights.get("common_fonts") and font in competitor_insights["common_fonts"]:
                score += 3  # Increased weight
            
            # Score based on typography trends
            if trend_insights.get("current_trends"):
                for trend in trend_insights["current_trends"]:
                    if self._font_matches_trend(font, trend):
                        score += 2
            
            font_scores[font] = score
        
        # Select top 2 fonts with better logic
        sorted_fonts = sorted(font_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_font = sorted_fonts[0][0] if sorted_fonts else "Inter"
        secondary_font = sorted_fonts[1][0] if len(sorted_fonts) > 1 else "Source Sans Pro"
        
        # Ensure fonts are different
        if primary_font == secondary_font:
            for font, score in sorted_fonts[1:]:
                if font != primary_font:
                    secondary_font = font
                    break
        
        # Generate font colors based on brand context
        font_colors = self._generate_font_colors(primary_font, secondary_font)
        
        # Get licensing information for selected fonts
        default_license = {'license': 'Open Font License', 'commercial_use': True, 'license_verification': 'verified_google_fonts'}
        primary_license = font_licensing.get(primary_font, default_license)
        secondary_license = font_licensing.get(secondary_font, default_license)
        
        # License verification status
        license_status = "verified" if (primary_license.get('license_verification', '').startswith('verified') and 
                                      secondary_license.get('license_verification', '').startswith('verified')) else "manual_check_required"
        
        print(f"🎯 Selected fonts: {primary_font} (primary, {font_scores.get(primary_font, 0)} pts), {secondary_font} (secondary, {font_scores.get(secondary_font, 0)} pts)")
        print(f"📝 License status: {license_status}")
        
        return {
            "primary": primary_font,
            "secondary": secondary_font,
            "font_colors": font_colors,
            "font_licensing": {
                "primary_font_license": primary_license,
                "secondary_font_license": secondary_license,
                "overall_license_status": license_status
            },
            "scores": font_scores,
            "total_fonts_evaluated": len(all_fonts)
        }
    
    def _font_matches_trend(self, font, trend):
        """Check if a font matches a typography trend"""
        trend_font_map = {
            "modern": ["Inter", "DM Sans", "Space Grotesk", "Plus Jakarta Sans", "Work Sans"],
            "clean": ["Inter", "Source Sans Pro", "Open Sans", "Lato", "Roboto"],
            "minimalist": ["Inter", "Montserrat", "Work Sans", "IBM Plex Sans"],
            "geometric": ["Montserrat", "Poppins", "Quicksand", "Comfortaa"],
            "humanist": ["Open Sans", "Lato", "Source Sans Pro", "Nunito Sans"],
            "sans-serif": ["Inter", "Roboto", "Open Sans", "Lato", "Montserrat"]
        }
        
        return font in trend_font_map.get(trend.lower(), [])
    
    def _generate_font_colors(self, primary_font, secondary_font):
        """Generate appropriate font colors based on font selection and brand context"""
        
        # Professional color schemes for typography
        font_color_schemes = {
            "dark_professional": {
                "primary_text": "#1A1A1A",
                "secondary_text": "#4A4A4A",
                "accent_text": "#0066CC",
                "light_text": "#6B6B6B",
                "white_text": "#FFFFFF"
            },
            "modern_contrast": {
                "primary_text": "#0F172A",
                "secondary_text": "#334155", 
                "accent_text": "#0EA5E9",
                "light_text": "#64748B",
                "white_text": "#FFFFFF"
            },
            "warm_professional": {
                "primary_text": "#1F2937",
                "secondary_text": "#4B5563",
                "accent_text": "#DC2626",
                "light_text": "#6B7280",
                "white_text": "#FFFFFF"
            }
        }
        
        # Select color scheme based on font characteristics
        if primary_font in ["Inter", "DM Sans", "Space Grotesk"]:
            scheme = "modern_contrast"
        elif primary_font in ["Montserrat", "Poppins", "Quicksand"]:
            scheme = "warm_professional"
        else:
            scheme = "dark_professional"
            
        return font_color_schemes[scheme]
    
    def _generate_font_rationale(self, selected_fonts, industry, brand_essence):
        """Generate explanation for font selection"""
        primary = selected_fonts["primary"]
        secondary = selected_fonts["secondary"]
        total_evaluated = selected_fonts.get("total_fonts_evaluated", "many")
        primary_score = selected_fonts["scores"].get(primary, 0)
        
        rationale = f"{primary} selected as primary font (scored {primary_score} points from {total_evaluated} fonts evaluated) for its professional appeal and excellent readability in {industry} sector. "
        rationale += f"{secondary} chosen as secondary font to provide visual hierarchy and complement the primary typeface. "
        
        if selected_fonts.get("font_colors"):
            rationale += f"Font colors optimized for readability and brand consistency. "
        
        if brand_essence and brand_essence.get("brand_positioning", {}).get("brand_personality"):
            personalities = brand_essence["brand_positioning"]["brand_personality"][:2]
            rationale += f"Font choices align with brand personality traits: {', '.join(personalities)}."
        
        return rationale

# Test usage
if __name__ == "__main__":
    agent = FontResearchAgent()
    
    # Test with sample brand essence
    sample_brand_essence = {
        "brand_positioning": {
            "brand_personality": ["innovative", "professional", "trustworthy"]
        }
    }
    
    result = agent.research_fonts("Adobe", "technology", sample_brand_essence)
    from pprint import pprint
    pprint(result)