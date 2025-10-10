"""
Company Research Agent for Illustration Generation
Conducts comprehensive web research to personalize brand illustrations
"""

import os
import json
import requests
from decouple import config
from datetime import datetime
import time

class CompanyResearchAgent:
    """
    Conducts deep web research about companies to inform 
    personalized illustration generation
    """
    
    def __init__(self):
        self.serper_api_key = config('SERPER_API_KEY')
        self.base_url = "https://google.serper.dev/search"
        
    def research_company_for_illustrations(self, company_name, industry, values=None, audience=None):
        """
        Comprehensive company research for illustration personalization
        
        Returns:
        {
            'company_context': {...},
            'industry_visuals': {...}, 
            'unique_elements': {...},
            'visual_inspiration': {...}
        }
        """
        print(f"🔍 Conducting deep research for {company_name} illustrations...")
        
        research_results = {
            'company_context': self._research_company_context(company_name, industry),
            'industry_visuals': self._research_industry_visuals(industry),
            'unique_elements': self._extract_unique_elements(company_name, industry),
            'visual_inspiration': self._find_visual_inspiration(company_name, industry),
            'competitor_analysis': self._analyze_competitors(company_name, industry)
        }
        
        # Process and synthesize research
        processed_research = self._synthesize_research(research_results, company_name, industry)
        
        print(f"✅ Research complete: {len(processed_research.get('illustration_concepts', []))} unique concepts identified")
        return processed_research
        
    def _research_company_context(self, company_name, industry):
        """Research company background, mission, products, recent news"""
        print(f"  📋 Researching company context for {company_name}...")
        
        searches = [
            f'"{company_name}" company mission vision values about',
            f'"{company_name}" products services offerings what we do',
            f'"{company_name}" company story history founding',
            f'"{company_name}" news recent developments 2024 2025'
        ]
        
        context = {
            'mission_vision': "",
            'products_services': "",
            'company_story': "",
            'recent_news': "",
            'key_terms': [],
            'unique_offerings': []
        }
        
        for search_query in searches:
            try:
                results = self._perform_search(search_query)
                if results:
                    # Extract relevant information from search results
                    search_type = self._classify_search_type(search_query)
                    context[search_type] = self._extract_relevant_content(results, search_type)
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"    ⚠️ Search failed for '{search_query}': {e}")
                continue
                
        return context
        
    def _research_industry_visuals(self, industry):
        """Research industry-specific visual trends and standards"""
        print(f"  🎨 Researching visual trends for {industry} industry...")
        
        searches = [
            f'"{industry}" industry visual design trends 2024 2025',
            f'"{industry}" companies logo design examples inspiration',
            f'"{industry}" brand illustration style modern professional',
            f'"{industry}" visual identity design best practices'
        ]
        
        visual_data = {
            'design_trends': [],
            'common_elements': [],
            'color_trends': [],
            'style_preferences': [],
            'visual_metaphors': []
        }
        
        for search_query in searches:
            try:
                results = self._perform_search(search_query)
                if results:
                    visual_insights = self._extract_visual_insights(results, industry)
                    self._merge_visual_data(visual_data, visual_insights)
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"    ⚠️ Visual research failed for '{search_query}': {e}")
                continue
                
        return visual_data
        
    def _extract_unique_elements(self, company_name, industry):
        """Identify unique company elements that could be visualized"""
        print(f"  💎 Extracting unique elements for {company_name}...")
        
        searches = [
            f'"{company_name}" unique selling proposition what makes different',
            f'"{company_name}" customer experience process journey',
            f'"{company_name}" innovation technology methodology approach',
            f'"{company_name}" vs competitors comparison advantages'
        ]
        
        unique_elements = {
            'differentiators': [],
            'processes': [],
            'innovations': [],
            'customer_journey': [],
            'competitive_advantages': []
        }
        
        for search_query in searches:
            try:
                results = self._perform_search(search_query)
                if results:
                    elements = self._extract_unique_business_elements(results)
                    self._merge_unique_elements(unique_elements, elements)
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"    ⚠️ Unique elements search failed: {e}")
                continue
                
        return unique_elements
        
    def _find_visual_inspiration(self, company_name, industry):
        """Find visual inspiration and style references"""
        print(f"  🎭 Finding visual inspiration for {company_name}...")
        
        searches = [
            f'"{company_name}" website design visual style interface',
            f'"{company_name}" social media visual content style',
            f'"{industry}" successful brands visual identity examples',
            f'"{industry}" illustration examples marketing materials'
        ]
        
        inspiration = {
            'style_references': [],
            'color_insights': [],
            'visual_approaches': [],
            'successful_examples': []
        }
        
        for search_query in searches:
            try:
                results = self._perform_search(search_query)
                if results:
                    visual_refs = self._extract_visual_references(results)
                    self._merge_visual_inspiration(inspiration, visual_refs)
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"    ⚠️ Visual inspiration search failed: {e}")
                continue
                
        return inspiration
        
    def _analyze_competitors(self, company_name, industry):
        """Analyze competitor visual approaches for differentiation"""
        print(f"  🏢 Analyzing competitors for differentiation...")
        
        search_query = f'"{company_name}" competitors {industry} main rivals companies'
        
        competitor_analysis = {
            'main_competitors': [],
            'visual_gaps': [],
            'differentiation_opportunities': []
        }
        
        try:
            results = self._perform_search(search_query)
            if results:
                competitor_analysis = self._extract_competitor_insights(results, industry)
                
        except Exception as e:
            print(f"    ⚠️ Competitor analysis failed: {e}")
            
        return competitor_analysis
        
    def _perform_search(self, query):
        """Perform web search using Serper API"""
        try:
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': 5,  # Limit results for efficiency
                'hl': 'en',
                'gl': 'us'
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"    ⚠️ Search API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"    ⚠️ Search request failed: {e}")
            return None
            
    def _synthesize_research(self, research_results, company_name, industry):
        """Synthesize all research into actionable illustration concepts"""
        print(f"  🧠 Synthesizing research into illustration concepts...")
        
        # Combine all research data
        company_context = research_results.get('company_context', {})
        industry_visuals = research_results.get('industry_visuals', {})
        unique_elements = research_results.get('unique_elements', {})
        visual_inspiration = research_results.get('visual_inspiration', {})
        competitor_analysis = research_results.get('competitor_analysis', {})
        
        # Generate company-specific illustration concepts
        illustration_concepts = self._generate_research_based_concepts(
            company_name, industry, company_context, unique_elements, visual_inspiration
        )
        
        # Create visual style guidelines based on research
        style_guidelines = self._create_style_guidelines(
            industry_visuals, visual_inspiration, competitor_analysis
        )
        
        synthesized = {
            'illustration_concepts': illustration_concepts,
            'style_guidelines': style_guidelines,
            'key_terms': self._extract_key_terminology(company_context, unique_elements),
            'visual_elements': self._compile_visual_elements(industry_visuals, visual_inspiration),
            'differentiation_strategy': self._define_differentiation_strategy(competitor_analysis)
        }
        
        return synthesized
        
    def _generate_research_based_concepts(self, company_name, industry, context, unique_elements, inspiration):
        """Generate illustration concepts based on actual research findings"""
        concepts = []
        
        # Concept 1: Company's Unique Value Proposition
        if unique_elements.get('differentiators'):
            concepts.append({
                'title': f"{company_name}'s Unique Approach",
                'description': f"Visual representation of what makes {company_name} different in the {industry} space",
                'metaphor': f"Based on research: {', '.join(unique_elements['differentiators'][:2])}",
                'research_basis': unique_elements['differentiators']
            })
            
        # Concept 2: Customer Journey/Process
        if unique_elements.get('customer_journey') or unique_elements.get('processes'):
            journey_elements = unique_elements.get('customer_journey', []) + unique_elements.get('processes', [])
            concepts.append({
                'title': f"{company_name} Customer Experience",
                'description': f"Illustration of the customer journey and experience with {company_name}",
                'metaphor': f"Process visualization: {', '.join(journey_elements[:2])}",
                'research_basis': journey_elements
            })
            
        # Concept 3: Innovation/Technology Focus
        if unique_elements.get('innovations'):
            concepts.append({
                'title': f"{company_name} Innovation",
                'description': f"Visual showcase of {company_name}'s innovative approach and technology",
                'metaphor': f"Innovation metaphor: {', '.join(unique_elements['innovations'][:2])}",
                'research_basis': unique_elements['innovations']
            })
            
        # Concept 4: Industry-Specific Value Creation
        concepts.append({
            'title': f"{company_name} in {industry}",
            'description': f"How {company_name} creates value specifically in the {industry} industry",
            'metaphor': f"Industry-specific value creation and impact visualization",
            'research_basis': context.get('products_services', '')
        })
        
        return concepts[:4]  # Return top 4 concepts
        
    # Helper methods for data extraction and processing
    def _classify_search_type(self, query):
        """Classify search query type for proper data extraction"""
        if 'mission vision values' in query:
            return 'mission_vision'
        elif 'products services' in query:
            return 'products_services'
        elif 'story history' in query:
            return 'company_story'
        elif 'news recent' in query:
            return 'recent_news'
        return 'general'
        
    def _extract_relevant_content(self, results, search_type):
        """Extract relevant content from search results based on type"""
        content = ""
        
        # Extract from organic results
        for result in results.get('organic', [])[:3]:  # Top 3 results
            snippet = result.get('snippet', '')
            content += snippet + " "
            
        return content.strip()[:500]  # Limit content length
        
    def _extract_visual_insights(self, results, industry):
        """Extract visual design insights from search results"""
        insights = {
            'trends': [],
            'elements': [],
            'styles': []
        }
        
        # Extract visual-related terms from snippets
        for result in results.get('organic', [])[:3]:
            snippet = result.get('snippet', '').lower()
            
            # Look for trend keywords
            trend_keywords = ['trend', 'modern', 'minimalist', 'bold', 'clean', 'professional']
            for keyword in trend_keywords:
                if keyword in snippet:
                    insights['trends'].append(keyword)
                    
        return insights
        
    def _extract_unique_business_elements(self, results):
        """Extract unique business elements from search results"""
        elements = []
        
        for result in results.get('organic', [])[:3]:
            snippet = result.get('snippet', '')
            # Extract key phrases that indicate unique elements
            elements.append(snippet[:100])  # First 100 chars as summary
            
        return elements
        
    def _extract_visual_references(self, results):
        """Extract visual style references from search results"""
        references = []
        
        for result in results.get('organic', [])[:2]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            references.append({
                'source': title,
                'description': snippet[:150]
            })
            
        return references
        
    def _extract_competitor_insights(self, results, industry):
        """Extract competitor analysis insights"""
        insights = {
            'competitors': [],
            'market_positioning': []
        }
        
        for result in results.get('organic', [])[:3]:
            snippet = result.get('snippet', '')
            insights['market_positioning'].append(snippet[:100])
            
        return insights
        
    def _merge_visual_data(self, target, source):
        """Merge visual data from multiple sources"""
        for key in source:
            if key in target and isinstance(target[key], list):
                target[key].extend(source[key])
                
    def _merge_unique_elements(self, target, source):
        """Merge unique elements data"""
        if isinstance(source, list):
            target['differentiators'].extend(source)
            
    def _merge_visual_inspiration(self, target, source):
        """Merge visual inspiration data"""
        if isinstance(source, list):
            target['style_references'].extend(source)
            
    def _create_style_guidelines(self, industry_visuals, visual_inspiration, competitor_analysis):
        """Create style guidelines based on research"""
        guidelines = {
            'recommended_styles': industry_visuals.get('style_preferences', []),
            'color_direction': industry_visuals.get('color_trends', []),
            'visual_approach': 'professional, modern, industry-appropriate',
            'differentiation_notes': competitor_analysis.get('visual_gaps', [])
        }
        return guidelines
        
    def _extract_key_terminology(self, context, unique_elements):
        """Extract key terminology for use in prompts"""
        terms = []
        
        # Extract from mission/vision
        mission_text = context.get('mission_vision', '')
        # Simple keyword extraction (could be enhanced with NLP)
        terms.extend([word for word in mission_text.split() if len(word) > 5][:5])
        
        return list(set(terms))  # Remove duplicates
        
    def _compile_visual_elements(self, industry_visuals, visual_inspiration):
        """Compile visual elements for prompt generation"""
        elements = {
            'style_keywords': industry_visuals.get('design_trends', []),
            'visual_metaphors': industry_visuals.get('visual_metaphors', []),
            'inspiration_sources': visual_inspiration.get('style_references', [])
        }
        return elements
        
    def _define_differentiation_strategy(self, competitor_analysis):
        """Define how to visually differentiate from competitors"""
        strategy = {
            'avoid_common_elements': competitor_analysis.get('visual_gaps', []),
            'emphasize_uniqueness': True,
            'focus_areas': ['innovation', 'customer_experience', 'value_proposition']
        }
        return strategy

    def save_research_results(self, research_data, company_name):
        """Save research results for future reference"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"output/{company_name.lower().replace(' ', '_')}_research_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(research_data, f, indent=2)
            print(f"  💾 Research results saved: {filename}")
        except Exception as e:
            print(f"  ⚠️ Failed to save research results: {e}")