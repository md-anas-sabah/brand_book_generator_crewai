import requests
import os
from datetime import datetime
import json
import uuid
import fal_client as fal
from decouple import config

def generate_logo_variations(company_name, industry, style, num_variations=3):
    """
    Calls FAL API using fal_client to generate logo variations with Ideogram V2A.
    Returns list of saved local file paths to generated logos.
    """
    try:
        # Ensure FAL_KEY is set in environment (matching first code pattern)
        os.environ['FAL_KEY'] = config('FAL_KEY')
        
        # Create output directory
        os.makedirs("output", exist_ok=True)
        
        logo_variations = []
        
        for i in range(num_variations):
            try:
                # Create detailed prompt for logo generation - ALWAYS enforce PURE black background
                prompt = (
                    f"Professional logo design for {company_name}, {industry} industry. "
                    f"Style: {style}. Clean, simple, modern vector design. "
                    f"MUST have transparent background only (no white, no black, no color fills). "
                    f"Flat design, no gradients, no shadows, no glow effects, no texture. "
                    f"High-resolution, suitable for corporate branding and scaling."
                )
                
                # Submit request to Ideogram V2A Turbo - enforce black background
                result = fal.run(
                    "fal-ai/ideogram/v2a/turbo",
                    arguments={
                        "prompt": prompt,
                        "aspect_ratio": "1:1",  # Square format for logos
                        "expand_prompt": True,
                        "style": "auto",
                        "negative_prompt": "white background, colored background, transparent background, gradient background, textured background, shadows, glow effects, lighting effects, reflections, gradients, orange glow, blue glow, any colored lighting"
                    }
                )
                
                image_url = result['images'][0]['url']
                
                # Download and save the image locally
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    # Create unique filename with timestamp (matching first code pattern)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"{company_name.lower().replace(' ', '_')}_logo_{i+1}_{timestamp}_{unique_id}.png"
                    local_path = os.path.join("output", filename)
                    
                    with open(local_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    logo_info = {
                        "variation_number": i + 1,
                        "image_url": image_url,
                        "local_path": local_path,
                        "filename": filename,
                        "prompt": prompt,
                        "company_name": company_name,
                        "industry": industry,
                        "style": style,
                        "seed": result.get('seed')
                    }
                    
                    logo_variations.append(logo_info)
                    print(f"Saved logo variation {i+1}: {local_path}")
                    
                else:
                    error_info = {
                        "variation_number": i + 1,
                        "image_url": image_url,
                        "local_path": "Failed to download",
                        "filename": "Failed to download",
                        "prompt": prompt,
                        "error": f"Failed to download image: {image_response.status_code}"
                    }
                    logo_variations.append(error_info)
                    print(f"Failed to download logo variation {i+1}")
                    
            except Exception as e:
                error_info = {
                    "variation_number": i + 1,
                    "image_url": "Error",
                    "local_path": "Error",
                    "filename": "Error",
                    "prompt": f"Logo for {company_name}",
                    "error": f"Error generating logo variation {i+1}: {str(e)}"
                }
                logo_variations.append(error_info)
                print(f"Error generating logo variation {i+1}: {str(e)}")
        
        # Return summary in JSON format (matching first code pattern)
        result_summary = {
            "logo_variations": logo_variations,
            "total_requested": num_variations,
            "successful_generations": len([logo for logo in logo_variations if "error" not in logo]),
            "company_name": company_name,
            "industry": industry,
            "style": style
        }
        
        # Extract just the file paths for backward compatibility
        successful_paths = [logo["local_path"] for logo in logo_variations if "error" not in logo and logo["local_path"] != "Failed to download"]
        
        print(f"\nGeneration Summary:")
        print(f"Total requested: {num_variations}")
        print(f"Successfully generated: {len(successful_paths)}")
        print(f"Generated logo files: {successful_paths}")
        
        return successful_paths
        
    except Exception as e:
        print(f"[FAL ERROR]: Error in logo generation process: {str(e)}")
        return []

def generate_logo_variations_detailed(company_name, industry, style, num_variations=3):
    """
    Same as generate_logo_variations but returns detailed JSON response
    matching the pattern from the first code.
    """
    try:
        # Ensure FAL_KEY is set in environment
        os.environ['FAL_KEY'] = config('FAL_KEY')
        
        # Create output directory
        os.makedirs("output", exist_ok=True)
        
        logo_variations = []
        
        for i in range(num_variations):
            try:
                prompt = (
                    f"Professional logo design for {company_name}, {industry} industry. "
                    f"Style: {style}. Clean, modern, minimalistic design. "
                    f"MUST HAVE solid pure black background (#000000), flat black background, "
                    f"NO gradients, NO shadows, NO glow effects, NO texture on background. "
                    f"Logo on completely flat solid black background only. "
                    f"Simple logo design with pure black background, high-resolution, corporate branding."
                )
                
                result = fal.run(
                    "fal-ai/ideogram/v2a/turbo",
                    arguments={
                        "prompt": prompt,
                        "aspect_ratio": "1:1",
                        "expand_prompt": True,
                        "style": "auto",
                        "negative_prompt": "white background, colored background, transparent background, gradient background, textured background, shadows, glow effects, lighting effects, reflections, gradients, orange glow, blue glow, any colored lighting"
                    }
                )
                
                image_url = result['images'][0]['url']
                image_response = requests.get(image_url)
                
                if image_response.status_code == 200:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"{company_name.lower().replace(' ', '_')}_logo_{i+1}_{timestamp}_{unique_id}.png"
                    local_path = os.path.join("output", filename)
                    
                    with open(local_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    logo_variations.append({
                        "variation_number": i + 1,
                        "image_url": image_url,
                        "local_path": local_path,
                        "filename": filename,
                        "prompt": prompt,
                        "company_name": company_name,
                        "industry": industry,
                        "style": style,
                        "seed": result.get('seed')
                    })
                else:
                    logo_variations.append({
                        "variation_number": i + 1,
                        "image_url": image_url,
                        "local_path": "Failed to download",
                        "filename": "Failed to download",
                        "prompt": prompt,
                        "error": f"Failed to download image: {image_response.status_code}"
                    })
                    
            except Exception as e:
                logo_variations.append({
                    "variation_number": i + 1,
                    "image_url": "Error",
                    "local_path": "Error",
                    "filename": "Error",
                    "prompt": f"Logo for {company_name}",
                    "error": f"Error generating logo variation {i+1}: {str(e)}"
                })
        
        return json.dumps({
            "logo_variations": logo_variations,
            "total_requested": num_variations,
            "successful_generations": len([logo for logo in logo_variations if "error" not in logo]),
            "company_name": company_name,
            "industry": industry,
            "style": style
        })
                
    except Exception as e:
        return json.dumps({
            "logo_variations": [],
            "total_requested": num_variations,
            "successful_generations": 0,
            "error": f"Error in logo generation process: {str(e)}"
        })

def generate_brand_illustrations(company_name, industry, values, audience, brand_essence="", num_illustrations=6):
    """
    Generate brand illustrations using Fal.ai Ideogram v3 model.
    Creates dynamic illustrations based on company research and brand essence.
    Includes web search research for industry-specific visual concepts.
    """
    try:
        # Ensure FAL_KEY is set in environment
        os.environ['FAL_KEY'] = config('FAL_KEY')
        
        # Create output directory
        os.makedirs("output", exist_ok=True)
        
        illustrations = []
        
        # Get industry-specific illustration concepts through web search
        illustration_concepts = _research_industry_illustrations(company_name, industry, values, audience)
        
        # Fallback to default concepts if research fails
        if not illustration_concepts:
            illustration_concepts = [
                f"{industry} innovation and growth visualization, representing {company_name} forward-thinking approach",
                f"Team collaboration in {industry} industry, showcasing {company_name} company culture and teamwork",
                f"Digital transformation concept for {industry} business, illustrating {company_name} modern approach",
                f"Customer success and satisfaction in {industry} sector, representing {company_name} client focus",
                f"Sustainable business practices visualization for {industry} company like {company_name}",
                f"Technology and innovation merge in {industry} environment, showcasing {company_name} expertise"
            ]
        
        for i, concept in enumerate(illustration_concepts[:num_illustrations]):
            try:
                # Create detailed prompt incorporating brand essence and research
                base_prompt = (
                    f"{concept}. "
                    f"Professional business illustration style, clean vector design. "
                    f"Color palette: ULTRAMARINE blue dominant theme, modern corporate aesthetic. "
                    f"Target audience: {audience}. "
                    f"Core values represented: {values}. "
                )
                
                if brand_essence:
                    base_prompt += f"Brand essence: {brand_essence}. "
                
                base_prompt += (
                    "DESIGN style: minimalistic, professional, business-focused. "
                    "Flat design approach, geometric shapes, clean lines, no gradients or shadows. "
                    "Corporate illustration suitable for brand book presentation."
                )
                
                # Submit request to Ideogram v3
                result = fal.run(
                    "fal-ai/ideogram/v3",
                    arguments={
                        "prompt": base_prompt,
                        "aspect_ratio": "16:9",  # Wide format for presentations
                        "expand_prompt": True,
                        "style": "DESIGN",
                        "color_palette_name": "ULTRAMARINE"
                    }
                )
                
                image_url = result['images'][0]['url']
                
                # Download and save the image locally
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    # Create unique filename with timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"{company_name.lower().replace(' ', '_')}_illustration_{i+1}_{timestamp}_{unique_id}.png"
                    local_path = os.path.join("output", filename)
                    
                    with open(local_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    illustration_info = {
                        "illustration_number": i + 1,
                        "concept": concept,
                        "image_url": image_url,
                        "local_path": local_path,
                        "filename": filename,
                        "prompt": base_prompt,
                        "company_name": company_name,
                        "industry": industry,
                        "seed": result.get('seed')
                    }
                    
                    illustrations.append(illustration_info)
                    print(f"Generated illustration {i+1}: {concept[:50]}...")
                    
                else:
                    error_info = {
                        "illustration_number": i + 1,
                        "concept": concept,
                        "image_url": image_url,
                        "local_path": "Failed to download",
                        "filename": "Failed to download",
                        "prompt": base_prompt,
                        "error": f"Failed to download image: {image_response.status_code}"
                    }
                    illustrations.append(error_info)
                    print(f"Failed to download illustration {i+1}")
                    
            except Exception as e:
                error_info = {
                    "illustration_number": i + 1,
                    "concept": concept,
                    "image_url": "Error",
                    "local_path": "Error",
                    "filename": "Error",
                    "prompt": f"Illustration for {company_name}",
                    "error": f"Error generating illustration {i+1}: {str(e)}"
                }
                illustrations.append(error_info)
                print(f"Error generating illustration {i+1}: {str(e)}")
        
        # Return summary
        result_summary = {
            "illustrations": illustrations,
            "total_requested": num_illustrations,
            "successful_generations": len([ill for ill in illustrations if "error" not in ill]),
            "company_name": company_name,
            "industry": industry,
            "style": "DESIGN",
            "color_palette": "ULTRAMARINE"
        }
        
        # Extract successful file paths
        successful_paths = [ill["local_path"] for ill in illustrations if "error" not in ill and ill["local_path"] != "Failed to download"]
        
        print(f"\nIllustration Generation Summary:")
        print(f"Total requested: {num_illustrations}")
        print(f"Successfully generated: {len(successful_paths)}")
        
        return result_summary
        
    except Exception as e:
        print(f"[FAL ERROR]: Error in illustration generation process: {str(e)}")
        return {
            "illustrations": [],
            "total_requested": num_illustrations,
            "successful_generations": 0,
            "error": f"Error in illustration generation process: {str(e)}"
        }

def _research_industry_illustrations(company_name, industry, values, audience):
    """
    Research industry-specific illustration concepts using web search.
    Returns dynamic illustration concepts based on current industry trends.
    """
    try:
        serper_api_key = os.getenv("SERPER_API_KEY")
        
        if serper_api_key:
            print("🌐 Researching industry-specific illustration trends...")
            
            # Search for industry illustration trends and concepts
            search_query = f"{industry} industry business illustrations visual concepts 2024 trends corporate design"
            search_results = _web_search(search_query, serper_api_key)
            
            if search_results:
                # Analyze search results to create dynamic concepts
                concepts = _analyze_illustration_research(search_results, company_name, industry, values, audience)
                if concepts:
                    print(f"✅ Generated {len(concepts)} research-based illustration concepts")
                    return concepts
            
            print("⚠️ Web search didn't yield specific concepts, using enhanced defaults")
            return _get_enhanced_default_concepts(company_name, industry, values, audience)
        else:
            print("⚠️ No Serper API key found, using enhanced default concepts")
            return _get_enhanced_default_concepts(company_name, industry, values, audience)
            
    except Exception as e:
        print(f"❌ Illustration research failed: {e}")
        return _get_enhanced_default_concepts(company_name, industry, values, audience)

def _web_search(query, api_key):
    """Perform web search for illustration research"""
    try:
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': api_key,
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

def _analyze_illustration_research(search_results, company_name, industry, values, audience):
    """Analyze web research results to create industry-specific illustration concepts"""
    try:
        # Combine search results text
        research_text = ""
        for result in search_results[:3]:
            research_text += f"{result.get('title', '')} {result.get('snippet', '')} "
        
        # Extract industry-specific visual themes and concepts
        industry_keywords = _extract_industry_keywords(research_text, industry)
        value_keywords = _extract_value_keywords(values)
        
        # Generate concepts based on research findings
        concepts = []
        
        # Core business concepts enhanced with research insights
        if "digital" in research_text.lower() or "technology" in research_text.lower():
            concepts.append(f"Digital innovation in {industry} sector, showcasing {company_name} technological advancement and forward-thinking solutions")
        
        if "team" in research_text.lower() or "collaboration" in research_text.lower():
            concepts.append(f"Collaborative excellence in {industry} industry, representing {company_name} team-driven approach and {value_keywords}")
        
        if "growth" in research_text.lower() or "success" in research_text.lower():
            concepts.append(f"Business growth and success visualization for {industry}, illustrating {company_name} market leadership and {audience} focus")
        
        if "sustainable" in research_text.lower() or "environment" in research_text.lower():
            concepts.append(f"Sustainable practices in {industry} business, demonstrating {company_name} environmental responsibility and long-term vision")
        
        if "customer" in research_text.lower() or "client" in research_text.lower():
            concepts.append(f"Customer-centric approach in {industry}, highlighting {company_name} commitment to {audience} satisfaction and service excellence")
        
        if "innovation" in research_text.lower() or "creative" in research_text.lower():
            concepts.append(f"Creative innovation in {industry} landscape, showcasing {company_name} innovative solutions and industry expertise")
        
        # Ensure we have at least 6 concepts
        while len(concepts) < 6:
            concepts.extend(_get_enhanced_default_concepts(company_name, industry, values, audience))
            
        return concepts[:6]
        
    except Exception as e:
        print(f"❌ Research analysis failed: {e}")
        return []

def _extract_industry_keywords(text, industry):
    """Extract industry-specific keywords from research text"""
    industry_lower = industry.lower()
    text_lower = text.lower()
    
    keywords = []
    if "tech" in text_lower or "software" in text_lower:
        keywords.append("technological innovation")
    if "finance" in text_lower or "fintech" in text_lower:
        keywords.append("financial solutions")
    if "health" in text_lower or "medical" in text_lower:
        keywords.append("healthcare excellence")
    if "education" in text_lower:
        keywords.append("educational advancement")
    if "retail" in text_lower or "ecommerce" in text_lower:
        keywords.append("customer experience")
        
    return ", ".join(keywords) if keywords else f"{industry} expertise"

def _extract_value_keywords(values):
    """Extract value-based keywords for illustrations"""
    if not values:
        return "core principles"
    
    value_list = [v.strip() for v in values.split(',') if v.strip()]
    if len(value_list) >= 2:
        return f"{value_list[0]} and {value_list[1]}"
    elif len(value_list) == 1:
        return value_list[0]
    else:
        return "core values"

def _get_enhanced_default_concepts(company_name, industry, values, audience):
    """Get enhanced default illustration concepts when research is unavailable"""
    return [
        f"Professional excellence in {industry}, representing {company_name} commitment to quality and industry leadership",
        f"Innovative solutions for {industry} challenges, showcasing {company_name} problem-solving capabilities and expertise", 
        f"Strategic growth and development in {industry} sector, illustrating {company_name} vision for {audience} success",
        f"Collaborative teamwork and company culture, demonstrating {company_name} people-first approach and shared values",
        f"Technology integration and digital transformation, highlighting {company_name} modern approach to {industry} solutions",
        f"Customer success and satisfaction focus, representing {company_name} dedication to {audience} outcomes and relationships"
    ]

# Example test
if __name__ == "__main__":
    # Test the updated function
    logos = generate_logo_variations(
        company_name="Acme Corp",
        industry="Fintech",
        style="Minimalistic",
        num_variations=2
    )
    print("Generated logo files:", logos)
    
    # Test the detailed version
    print("\n" + "="*50)
    print("Detailed Response:")
    detailed_result = generate_logo_variations_detailed(
        company_name="Tech Solutions",
        industry="Software",
        style="Modern",
        num_variations=1
    )
    print(detailed_result)