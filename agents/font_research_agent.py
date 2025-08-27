import requests
import json
from tools.serper_search import search_google
from decouple import config

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
        
        # Create scoring system for fonts
        font_scores = {}
        all_fonts = ["Inter", "Source Sans Pro", "Open Sans", "Montserrat", "Poppins", "Lato", "Roboto", "IBM Plex Sans", "Nunito Sans"]
        
        for font in all_fonts:
            score = 0
            
            # Score based on industry relevance
            if font in industry_fonts:
                score += 3
            
            # Score based on personality alignment  
            if font in personality_fonts:
                score += 2
            
            # Score based on competitor research
            if competitor_insights.get("common_fonts") and font in competitor_insights["common_fonts"]:
                score += 1
            
            font_scores[font] = score
        
        # Select top 2 fonts
        sorted_fonts = sorted(font_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_font = sorted_fonts[0][0] if sorted_fonts else "Inter"
        secondary_font = sorted_fonts[1][0] if len(sorted_fonts) > 1 else "Source Sans Pro"
        
        # Ensure fonts are different
        if primary_font == secondary_font:
            secondary_font = "Source Sans Pro" if primary_font != "Source Sans Pro" else "Open Sans"
        
        return {
            "primary": primary_font,
            "secondary": secondary_font,
            "scores": font_scores
        }
    
    def _generate_font_rationale(self, selected_fonts, industry, brand_essence):
        """Generate explanation for font selection"""
        primary = selected_fonts["primary"]
        secondary = selected_fonts["secondary"]
        
        rationale = f"{primary} selected as primary font for its professional appeal and excellent readability in {industry} sector. "
        rationale += f"{secondary} chosen as secondary font to provide visual hierarchy and complement the primary typeface. "
        
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