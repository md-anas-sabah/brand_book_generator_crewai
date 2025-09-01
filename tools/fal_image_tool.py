import requests
import os
from datetime import datetime
import json
import uuid
import fal_client as fal
from decouple import config
from PIL import Image

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
                # Create detailed prompt for logo generation - enforce consistent white background
                prompt = (
                    f"Professional HD logo design for {company_name}, {industry} industry. "
                    f"Style: {style}. Minimal, modern, flat vector design. "
                    f"Pure white background (#FFFFFF). Clean white background only. "
                    f"Corporate logo on white background, no other background colors. "
                    f"Ultra-flat design, absolutely no gradients, no shadows, no glow effects, no texture, no 3D effects. "
                    f"4K high-resolution, crystal clear, scalable vector quality, perfect for corporate branding. "
                    f"White background mandatory for consistent processing."
                )
                
                # Submit request to Ideogram V2A Turbo - enforce white/transparent background
                result = fal.run(
                    "fal-ai/ideogram/v2a/turbo",
                    arguments={
                        "prompt": prompt,
                        "aspect_ratio": "1:1",  # Square format for logos
                        "expand_prompt": True,
                        "style": "auto",
                        "negative_prompt": "black background, dark background, colored background, gradient background, textured background, shadows, glow effects, lighting effects, reflections, gradients, orange glow, blue glow, any colored lighting, dark themes"
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
                    
                    # For logos, create both versions but don't auto-replace
                    # (logos often have text that gets removed with background)
                    transparent_path = white_to_transparent(local_path)
                    # Always use original for logos to preserve text and quality
                    logo_info_path = local_path
                    
                    logo_info = {
                        "variation_number": i + 1,
                        "image_url": image_url,
                        "local_path": logo_info_path,
                        "filename": filename,
                        "transparent_version": transparent_path if transparent_path else None,
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
                    f"Professional HD logo design for {company_name}, {industry} industry. "
                    f"Style: {style}. Minimal, modern, flat vector design. "
                    f"Pure white background (#FFFFFF). Clean white background only. "
                    f"Corporate logo on white background, no other background colors. "
                    f"Ultra-flat design, absolutely no gradients, no shadows, no glow effects, no texture, no 3D effects. "
                    f"4K high-resolution, crystal clear, scalable vector quality, perfect for corporate branding. "
                    f"White background mandatory for consistent processing."
                )
                
                result = fal.run(
                    "fal-ai/ideogram/v2a/turbo",
                    arguments={
                        "prompt": prompt,
                        "aspect_ratio": "1:1",
                        "expand_prompt": True,
                        "style": "auto",
                        "negative_prompt": "black background, dark background, colored background, gradient background, textured background, shadows, glow effects, lighting effects, reflections, gradients, orange glow, blue glow, any colored lighting, dark themes"
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
                    
                    # For logos, create both versions but preserve original
                    transparent_path = white_to_transparent(local_path)
                    logo_info_path = local_path  # Always use original for logos
                    
                    logo_variations.append({
                        "variation_number": i + 1,
                        "image_url": image_url,
                        "local_path": logo_info_path,
                        "filename": filename,
                        "transparent_version": transparent_path if transparent_path else None,
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
                # Create modern 2025 business illustration prompt
                base_prompt = (
                    f"{concept}. "
                    f"Modern 2025 business illustration style, inspired by Dribbble, Behance, and high-end corporate design. "
                    f"Vibrant gradient color palette with ULTRAMARINE blue accents, paired with clean neutrals. "
                    f"Smooth 3D isometric look, soft shadows, subtle depth, and glossy highlights for a premium feel. "
                    f"Target audience: {audience}. "
                    f"Core values represented: {values}. "
                )
                
                if brand_essence:
                    base_prompt += f"Brand essence: {brand_essence}. "
                
                base_prompt += (
                    "DESIGN style: futuristic, minimal yet dynamic, visually engaging, and human-centered. "
                    "Use contemporary vector-3D hybrid style, smooth gradients, rounded shapes, soft lighting. "
                    "PURE WHITE BACKGROUND (#FFFFFF) mandatory, modern illustration suitable for brand book, "
                    "presentation-ready, scalable high-quality asset."
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
                    
                    # Keep original for illustrations - they're meant to have backgrounds
                    illustration_info_path = local_path
                    
                    illustration_info = {
                        "illustration_number": i + 1,
                        "concept": concept,
                        "image_url": image_url,
                        "local_path": illustration_info_path,
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

def white_to_transparent(img_path):
    """
    Convert any background to transparent using AI background removal.
    Falls back to manual white/light background removal if rembg fails.
    Returns the new transparent image path, or None if failed.
    """
    try:
        # Method 1: Try AI-powered background removal with rembg
        try:
            from rembg import remove
            
            with open(img_path, 'rb') as input_file:
                input_data = input_file.read()
            
            output_data = remove(input_data)
            
            # Create transparent version filename
            transparent_path = img_path.replace('.png', '_transparent.png')
            with open(transparent_path, 'wb') as output_file:
                output_file.write(output_data)
            
            print(f"✅ Created AI-removed background version: {transparent_path}")
            return transparent_path
            
        except ImportError:
            print("⚠️ rembg not installed, trying manual background removal...")
            
        except Exception as e:
            print(f"⚠️ AI background removal failed: {e}, trying manual method...")
        
        # Method 2: Manual background removal for light backgrounds
        img = Image.open(img_path).convert("RGBA")
        datas = img.getdata()
        new_data = []

        for item in datas:
            # More flexible background detection - remove light colors and gradients
            r, g, b, a = item
            
            # Check if pixel is light/whitish/yellowish (common backgrounds)
            is_background = (
                # Very light colors (near white)
                (r > 240 and g > 240 and b > 240) or
                # Light yellow/orange (common AI backgrounds)
                (r > 200 and g > 180 and b < 150 and abs(r-g) < 80) or
                # Light gradients
                (r > 220 and g > 200 and b > 150)
            )
            
            if is_background:
                new_data.append((255, 255, 255, 0))  # Make transparent
            else:
                new_data.append(item)

        img.putdata(new_data)
        
        # Create transparent version filename
        transparent_path = img_path.replace('.png', '_transparent.png')
        img.save(transparent_path, "PNG")
        
        print(f"✅ Created manual background removal version: {transparent_path}")
        return transparent_path
        
    except Exception as e:
        print(f"❌ Failed to create transparent version: {e}")
        return None

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