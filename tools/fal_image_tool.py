import requests
import os
from datetime import datetime
import json
import uuid
import fal_client as fal
from decouple import config
from PIL import Image

def generate_logo_variations(company_name, industry, style, num_variations=3, logo_color=None):
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
                # Create logo prompt with aggressive white background and strong color enforcement
                color_instruction = ""
                negative_color_restrictions = "No yellow, no orange, no cream, no gray backgrounds allowed. "
                
                # Make the last variation black and white, others use the preferred color
                is_last_variation = (i == num_variations - 1)
                
                if is_last_variation:
                    # Last variation: black and white only
                    color_instruction = "Black and white logo ONLY. Logo elements in BLACK color on white background. Monochrome design. "
                    negative_color_restrictions += "No colored elements. No purple, no blue, no green, no red elements. "
                elif logo_color:
                    # Other variations: use the user's preferred color
                    color_instruction = f"ALL logo elements MUST be {logo_color} color ONLY. Logo text and symbols in {logo_color}. "
                    # Don't restrict the user's chosen color in negative prompt
                    if logo_color.lower() not in ["#000000", "#000", "black"]:
                        negative_color_restrictions += "No black text or elements. "
                else:
                    negative_color_restrictions += "No black text. "
                
                prompt = (
                    f"Logo for {company_name} on PLAIN SOLID WHITE BACKGROUND. {industry} industry. "
                    f"Style: {style}. Simple flat vector logo design. {color_instruction}"
                    f"PLAIN WHITE BACKGROUND ONLY. Pure white (#FFFFFF) background, completely plain, no patterns, no designs, no textures. "
                    f"{negative_color_restrictions}"
                    f"Flat design, no shadows, no 3D effects, no gradients anywhere. "
                    f"Clean simple logo on completely plain white background, vector quality."
                )
                
                # Create dynamic negative prompt that doesn't conflict with user's color choice
                negative_prompt_parts = [
                    "yellow background", "orange background", "gold background", "cream background", 
                    "beige background", "gray background", "grey background", "dark background", 
                    "colored background", "gradient background", "textured background", 
                    "shadows", "glow effects", "lighting effects", "reflections", "gradients", 
                    "any colored lighting", "dark themes"
                ]
                
                if is_last_variation:
                    # For black and white variation, restrict all colors
                    negative_prompt_parts.extend([
                        "purple elements", "blue elements", "green elements", "red elements", 
                        "colored text", "colored logo", "purple background", "blue background", 
                        "green background", "red background"
                    ])
                else:
                    # Add specific background color restrictions, but avoid the user's chosen color
                    if not logo_color or not any(color in logo_color.lower() for color in ["blue", "#0000ff", "#00f"]):
                        negative_prompt_parts.append("blue background")
                    if not logo_color or not any(color in logo_color.lower() for color in ["green", "#00ff00", "#0f0"]):
                        negative_prompt_parts.append("green background")
                    if not logo_color or not any(color in logo_color.lower() for color in ["red", "#ff0000", "#f00"]):
                        negative_prompt_parts.append("red background")
                    if not logo_color or not any(color in logo_color.lower() for color in ["purple", "#800080", "#810eb1"]):
                        negative_prompt_parts.append("purple background")
                    if not logo_color or not any(color in logo_color.lower() for color in ["black", "#000000", "#000"]):
                        negative_prompt_parts.append("black background")
                
                dynamic_negative_prompt = ", ".join(negative_prompt_parts)
                
                # Submit request to Ideogram V2A Turbo - enforce white/transparent background
                result = fal.run(
                    "fal-ai/ideogram/v2a/turbo",
                    arguments={
                        "prompt": prompt,
                        "aspect_ratio": "1:1",  # Square format for logos
                        "expand_prompt": True,
                        "style": "auto",
                        "negative_prompt": dynamic_negative_prompt
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

def generate_logo_variations_detailed(company_name, industry, style, num_variations=3, logo_color=None):
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
                # Create logo prompt with color enforcement (same logic as main function)
                color_instruction = ""
                negative_color_restrictions = "No yellow, no orange, no cream, no gray backgrounds allowed. "
                
                # Make the last variation black and white, others use the preferred color
                is_last_variation = (i == num_variations - 1)
                
                if is_last_variation:
                    # Last variation: black and white only
                    color_instruction = "Black and white logo ONLY. Logo elements in BLACK color on white background. Monochrome design. "
                    negative_color_restrictions += "No colored elements. No purple, no blue, no green, no red elements. "
                elif logo_color:
                    # Other variations: use the user's preferred color
                    color_instruction = f"ALL logo elements MUST be {logo_color} color ONLY. Logo text and symbols in {logo_color}. "
                    # Don't restrict the user's chosen color in negative prompt
                    if logo_color.lower() not in ["#000000", "#000", "black"]:
                        negative_color_restrictions += "No black text or elements. "
                else:
                    negative_color_restrictions += "No black text. "
                
                prompt = (
                    f"Logo for {company_name} on SOLID WHITE BACKGROUND. {industry} industry. "
                    f"Style: {style}. Simple flat vector logo design. {color_instruction}"
                    f"WHITE BACKGROUND ONLY. Pure white (#FFFFFF) background, no other colors. "
                    f"{negative_color_restrictions}"
                    f"Flat design, no shadows, no 3D effects, no gradients anywhere. "
                    f"Clean simple logo on pure white background, vector quality."
                )
                
                # Create dynamic negative prompt that doesn't conflict with user's color choice
                negative_prompt_parts = [
                    "yellow background", "orange background", "gold background", "cream background", 
                    "beige background", "gray background", "grey background", "dark background", 
                    "colored background", "gradient background", "textured background", 
                    "shadows", "glow effects", "lighting effects", "reflections", "gradients", 
                    "any colored lighting", "dark themes"
                ]
                
                if is_last_variation:
                    # For black and white variation, restrict all colors
                    negative_prompt_parts.extend([
                        "purple elements", "blue elements", "green elements", "red elements", 
                        "colored text", "colored logo", "purple background", "blue background", 
                        "green background", "red background"
                    ])
                else:
                    # Add specific background color restrictions, but avoid the user's chosen color
                    if not logo_color or not any(color in logo_color.lower() for color in ["blue", "#0000ff", "#00f"]):
                        negative_prompt_parts.append("blue background")
                    if not logo_color or not any(color in logo_color.lower() for color in ["green", "#00ff00", "#0f0"]):
                        negative_prompt_parts.append("green background")
                    if not logo_color or not any(color in logo_color.lower() for color in ["red", "#ff0000", "#f00"]):
                        negative_prompt_parts.append("red background")
                    if not logo_color or not any(color in logo_color.lower() for color in ["purple", "#800080", "#810eb1"]):
                        negative_prompt_parts.append("purple background")
                    if not logo_color or not any(color in logo_color.lower() for color in ["black", "#000000", "#000"]):
                        negative_prompt_parts.append("black background")
                
                dynamic_negative_prompt = ", ".join(negative_prompt_parts)
                
                result = fal.run(
                    "fal-ai/ideogram/v2a/turbo",
                    arguments={
                        "prompt": prompt,
                        "aspect_ratio": "1:1",
                        "expand_prompt": True,
                        "style": "auto",
                        "negative_prompt": dynamic_negative_prompt
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

def generate_brand_merchandise_with_logo(company_name, logo_image_path, brand_color="#000000"):
    """
    Generate brand merchandise mockups (t-shirts) using Flux Pro Kontext with image-to-image.
    Uses the actual logo from the first slide as reference image for editing.
    Creates 3 realistic t-shirt mockups: white, black, and yellow with the exact same logo.
    """
    try:
        # Ensure FAL_KEY is set in environment
        os.environ['FAL_KEY'] = config('FAL_KEY')
        
        # Create output directory
        os.makedirs("output", exist_ok=True)
        
        # Check if logo file exists
        if not os.path.exists(logo_image_path):
            print(f"❌ Logo file not found: {logo_image_path}")
            return None
        
        merchandise_images = {}
        
        # Define t-shirt configurations: (color_name, shirt_color, logo_color_description)
        shirt_configs = [
            ("White", "white", "black logo and text"),
            ("Black", "black", "white logo and text"), 
            ("Yellow", "yellow", "black logo and text")
        ]
        
        print(f"🎯 Using logo reference: {logo_image_path}")
        
        for color_name, shirt_color, logo_color_desc in shirt_configs:
            try:
                # Create editing instruction prompt for Kontext (editing-focused prompt)
                prompt = (
                    f"Transform this logo into a professional product photo: place it centered on a {shirt_color} t-shirt chest. "
                    f"Make the logo {logo_color_desc} on the t-shirt fabric. "
                    f"Create realistic merchandise mockup with natural fabric texture, proper lighting, "
                    f"clean studio background. Maintain logo clarity and professional e-commerce photo quality."
                )
                
                # Read logo image and convert to base64 for API
                with open(logo_image_path, 'rb') as img_file:
                    import base64
                    logo_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                    logo_data_url = f"data:image/png;base64,{logo_base64}"
                
                # Submit request to Flux Pro Kontext (correct image-to-image model)
                result = fal.run(
                    "fal-ai/flux-pro/kontext",
                    arguments={
                        "prompt": prompt,
                        "image_url": logo_data_url,  # Reference logo image for editing
                        "guidance_scale": 7.5,  # Prompt adherence strength (default for Kontext)
                        "num_inference_steps": 28,  # Generation steps
                        "seed": None,  # For reproducible results
                        "enable_safety_checker": True
                    }
                )
                
                image_url = result['images'][0]['url']
                
                # Download and save the image locally
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    # Create unique filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"{company_name.lower().replace(' ', '_')}_tshirt_{color_name.lower()}_{timestamp}_{unique_id}.png"
                    local_path = os.path.join("output", filename)
                    
                    with open(local_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    merchandise_images[color_name] = local_path
                    print(f"✅ Generated {color_name} t-shirt: {filename}")
                    
                else:
                    print(f"❌ Failed to download {color_name} t-shirt: {image_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error generating {color_name} t-shirt: {e}")
                continue
        
        if merchandise_images:
            result_summary = {
                "merchandise_images": merchandise_images,
                "total_requested": 3,
                "successful_generations": len(merchandise_images),
                "company_name": company_name,
                "brand_color": brand_color,
                "logo_reference": logo_image_path
            }
            
            print(f"\n🎉 Merchandise Generation Summary:")
            print(f"Successfully generated: {len(merchandise_images)} t-shirts")
            print(f"T-shirt colors: {list(merchandise_images.keys())}")
            print(f"Using logo reference: {logo_image_path}")
            
            return result_summary
        else:
            print("❌ No merchandise images were successfully generated")
            return None
            
    except Exception as e:
        print(f"[FAL ERROR]: Error in merchandise generation: {str(e)}")
        return None

def generate_brand_mugs_with_logo(company_name, logo_image_path, brand_color="#000000"):
    """
    Generate brand mug mockups using Flux Pro Kontext with image-to-image.
    Uses the actual logo from the first slide as reference image for editing.
    Creates 3 realistic mug mockups: white, black, and primary color with smart text color.
    """
    try:
        # Ensure FAL_KEY is set in environment
        os.environ['FAL_KEY'] = config('FAL_KEY')
        
        # Create output directory
        os.makedirs("output", exist_ok=True)
        
        # Check if logo file exists
        if not os.path.exists(logo_image_path):
            print(f"❌ Logo file not found: {logo_image_path}")
            return None
        
        # Smart color detection for primary color mug
        def is_light_color(hex_color):
            """Check if a color is light (needs black text) or dark (needs white text)"""
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            # Convert to RGB
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            # Calculate luminance (0-255)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b)
            return luminance > 128  # Light if > 128
        
        # Determine logo color for primary color mug
        primary_is_light = is_light_color(brand_color)
        primary_logo_color = "black logo and text" if primary_is_light else "white logo and text"
        
        mug_images = {}
        
        # Define mug configurations: (color_name, mug_color, logo_color_description)
        mug_configs = [
            ("White", "white", "black logo and text"),
            ("Black", "black", "white logo and text"), 
            ("Primary", brand_color, primary_logo_color)
        ]
        
        print(f"🎯 Using logo reference: {logo_image_path}")
        print(f"🎨 Primary color: {brand_color} ({'light' if primary_is_light else 'dark'}) - using {primary_logo_color}")
        
        for color_name, mug_color, logo_color_desc in mug_configs:
            try:
                # Create editing instruction prompt for Kontext (mug-focused)
                prompt = (
                    f"Transform this logo into a professional product photo: place it centered on a {mug_color} coffee mug. "
                    f"Make the logo {logo_color_desc} on the mug surface. "
                    f"Create realistic mug mockup with ceramic texture, proper lighting, "
                    f"clean studio background. Maintain logo clarity and professional e-commerce photo quality. "
                    f"Front view of the mug with handle visible."
                )
                
                # Read logo image and convert to base64 for API
                with open(logo_image_path, 'rb') as img_file:
                    import base64
                    logo_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                    logo_data_url = f"data:image/png;base64,{logo_base64}"
                
                # Submit request to Flux Pro Kontext
                result = fal.run(
                    "fal-ai/flux-pro/kontext",
                    arguments={
                        "prompt": prompt,
                        "image_url": logo_data_url,  # Reference logo image for editing
                        "guidance_scale": 7.5,  # Prompt adherence strength
                        "num_inference_steps": 28,  # Generation steps
                        "seed": None,  # For reproducible results
                        "enable_safety_checker": True
                    }
                )
                
                image_url = result['images'][0]['url']
                
                # Download and save the image locally
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    # Create unique filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"{company_name.lower().replace(' ', '_')}_mug_{color_name.lower()}_{timestamp}_{unique_id}.png"
                    local_path = os.path.join("output", filename)
                    
                    with open(local_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    mug_images[color_name] = local_path
                    print(f"✅ Generated {color_name} mug: {filename}")
                    
                else:
                    print(f"❌ Failed to download {color_name} mug: {image_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error generating {color_name} mug: {e}")
                continue
        
        if mug_images:
            result_summary = {
                "mug_images": mug_images,
                "total_requested": 3,
                "successful_generations": len(mug_images),
                "company_name": company_name,
                "brand_color": brand_color,
                "logo_reference": logo_image_path,
                "primary_color_is_light": primary_is_light
            }
            
            print(f"\n☕ Mug Generation Summary:")
            print(f"Successfully generated: {len(mug_images)} mugs")
            print(f"Mug colors: {list(mug_images.keys())}")
            print(f"Using logo reference: {logo_image_path}")
            
            return result_summary
        else:
            print("❌ No mug images were successfully generated")
            return None
            
    except Exception as e:
        print(f"[FAL ERROR]: Error in mug generation: {str(e)}")
        return None

def generate_professional_brand_illustrations(company_name, industry, values, audience, 
                                            brand_essence=None, primary_color="#810eb1", num_illustrations=4):
    """
    Generate professional brand illustrations using Recraft V3 following the 4-step process:
    1. Define Brand Personality
    2. Choose Illustration Style 
    3. Brainstorm Concepts and Metaphors
    4. Set the Rules
    """
    try:
        # Ensure FAL_KEY is set in environment
        os.environ['FAL_KEY'] = config('FAL_KEY')
        
        # Create output directory
        os.makedirs("output", exist_ok=True)
        
        print(f"🎨 Generating professional brand illustrations for {company_name}...")
        
        # STEP 1: Define Brand Personality (3-5 keywords)
        brand_personality = _analyze_brand_personality(industry, values, audience, brand_essence)
        print(f"✅ Brand Personality: {', '.join(brand_personality)}")
        
        # STEP 2: Choose Illustration Style
        illustration_style = _select_illustration_style(brand_personality, industry)
        print(f"✅ Illustration Style: {illustration_style}")
        
        # STEP 3: Brainstorm Concepts and Metaphors
        illustration_concepts = _generate_visual_concepts(company_name, industry, values, 
                                                        audience, brand_personality, num_illustrations)
        print(f"✅ Generated {len(illustration_concepts)} visual concepts")
        
        # STEP 4: Set the Rules
        illustration_rules = _define_illustration_rules(primary_color, illustration_style)
        print(f"✅ Illustration rules defined")
        
        illustrations = []
        
        for i, concept in enumerate(illustration_concepts):
            try:
                print(f"  Generating illustration {i+1}: {concept['title']}")
                
                # Create professional prompt following the rules
                prompt = _create_recraft_prompt(concept, illustration_style, illustration_rules, company_name)
                
                # Convert hex color to RGB for Recraft V3
                primary_rgb = _hex_to_rgb(primary_color)
                
                # Generate with Recraft V3
                result = fal.run(
                    "fal-ai/recraft/v3/text-to-image",
                    arguments={
                        "prompt": prompt,
                        "image_size": "landscape_16_9",  # Professional presentation format
                        "style": illustration_style,
                        "colors": [{"r": primary_rgb[0], "g": primary_rgb[1], "b": primary_rgb[2]}],
                        "enable_safety_checker": True
                    }
                )
                
                image_url = result['images'][0]['url']
                
                # Download the image
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    # Create unique filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"{company_name.lower().replace(' ', '_')}_illustration_{i+1}_{timestamp}_{unique_id}.png"
                    local_path = os.path.join("output", filename)
                    
                    with open(local_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    # Keep original image without background removal for illustrations
                    transparent_path = None
                    
                    illustration_info = {
                        "illustration_number": i + 1,
                        "title": concept['title'],
                        "concept": concept['description'],
                        "metaphor": concept['metaphor'],
                        "image_url": image_url,
                        "local_path": local_path,
                        "transparent_path": transparent_path,
                        "filename": filename,
                        "prompt": prompt,
                        "style": illustration_style,
                        "brand_personality": brand_personality,
                        "seed": result.get('seed')
                    }
                    
                    illustrations.append(illustration_info)
                    print(f"  ✅ Generated: {concept['title']}")
                    
                else:
                    print(f"  ❌ Failed to download illustration {i+1}")
                    
            except Exception as e:
                print(f"  ❌ Error generating illustration {i+1}: {e}")
                continue
        
        # Return comprehensive results
        result_summary = {
            "illustrations": illustrations,
            "brand_personality": brand_personality,
            "illustration_style": illustration_style,
            "illustration_rules": illustration_rules,
            "total_requested": num_illustrations,
            "successful_generations": len(illustrations),
            "company_name": company_name,
            "industry": industry,
            "primary_color": primary_color
        }
        
        print(f"\n🎉 Brand Illustration Generation Summary:")
        print(f"Total requested: {num_illustrations}")
        print(f"Successfully generated: {len(illustrations)}")
        print(f"Brand personality: {', '.join(brand_personality)}")
        print(f"Illustration style: {illustration_style}")
        
        return result_summary
        
    except Exception as e:
        print(f"[FAL ERROR]: Error in brand illustration generation: {str(e)}")
        return None

def _analyze_brand_personality(industry, values, audience, brand_essence):
    """Step 1: Define Brand Personality (3-5 keywords)"""
    personality_map = {
        # Tech/Software
        "technology": ["Modern", "Innovative", "Clean", "Technical", "Forward-thinking"],
        "software": ["Modern", "Innovative", "Clean", "Technical", "User-friendly"],
        "fintech": ["Trustworthy", "Modern", "Secure", "Professional", "Accessible"],
        
        # Food & Beverage
        "food": ["Warm", "Authentic", "Fresh", "Community-focused", "Inviting"],
        "beverage": ["Energizing", "Social", "Fresh", "Authentic", "Comforting"],
        "restaurant": ["Warm", "Welcoming", "Authentic", "Social", "Quality-focused"],
        "tea": ["Calming", "Authentic", "Traditional", "Mindful", "Comforting"],
        "coffee": ["Energizing", "Social", "Urban", "Quality-focused", "Modern"],
        
        # Healthcare
        "healthcare": ["Caring", "Professional", "Trustworthy", "Clean", "Accessible"],
        "medical": ["Professional", "Trustworthy", "Precise", "Caring", "Reliable"],
        
        # Education
        "education": ["Inspiring", "Accessible", "Growth-oriented", "Supportive", "Modern"],
        "learning": ["Engaging", "Accessible", "Progressive", "Supportive", "Interactive"],
        
        # Finance
        "finance": ["Trustworthy", "Professional", "Secure", "Reliable", "Forward-thinking"],
        "banking": ["Secure", "Professional", "Trustworthy", "Accessible", "Modern"],
        
        # Retail/E-commerce
        "retail": ["Accessible", "Trendy", "Customer-focused", "Quality-oriented", "Modern"],
        "ecommerce": ["Convenient", "Modern", "User-friendly", "Accessible", "Reliable"],
        
        # Default
        "default": ["Professional", "Modern", "Trustworthy", "Quality-focused", "Accessible"]
    }
    
    # Find industry match
    industry_lower = industry.lower()
    brand_personality = None
    
    for key in personality_map:
        if key in industry_lower:
            brand_personality = personality_map[key]
            break
    
    if not brand_personality:
        brand_personality = personality_map["default"]
    
    # Enhance with values if provided
    if values:
        value_keywords = []
        values_lower = values.lower()
        
        if any(word in values_lower for word in ["trust", "reliable", "honest"]):
            value_keywords.append("Trustworthy")
        if any(word in values_lower for word in ["innovate", "creative", "new"]):
            value_keywords.append("Innovative")
        if any(word in values_lower for word in ["simple", "clean", "minimal"]):
            value_keywords.append("Simple")
        if any(word in values_lower for word in ["luxury", "premium", "high-end"]):
            value_keywords.append("Luxurious")
        if any(word in values_lower for word in ["fun", "playful", "enjoy"]):
            value_keywords.append("Playful")
        if any(word in values_lower for word in ["tradition", "heritage", "classic"]):
            value_keywords.append("Traditional")
        
        # Merge and keep top 5
        combined = list(set(brand_personality + value_keywords))
        brand_personality = combined[:5]
    
    return brand_personality[:5]

def _select_illustration_style(brand_personality, industry):
    """Step 2: Choose Illustration Style based on personality"""
    
    # Style mapping based on brand personality
    if any(word in brand_personality for word in ["Modern", "Clean", "Technical"]):
        return "vector_illustration/thin"  # Minimalist Line Art
    elif any(word in brand_personality for word in ["Playful", "Social", "Energizing"]):
        return "digital_illustration/2d_art_poster"  # Flat Vector - colorful and friendly
    elif any(word in brand_personality for word in ["Authentic", "Traditional", "Warm"]):
        return "digital_illustration/hand_drawn"  # Hand-drawn/Textured
    elif any(word in brand_personality for word in ["Technical", "Professional", "Forward-thinking"]):
        return "vector_illustration/infographical"  # Isometric/Technical
    elif any(word in brand_personality for word in ["Luxurious", "Premium"]):
        return "digital_illustration/expressionism"  # Sophisticated style
    else:
        return "digital_illustration/2d_art_poster"  # Default friendly flat vector

def _generate_visual_concepts(company_name, industry, values, audience, brand_personality, num_concepts):
    """Step 3: Brainstorm Concepts and Metaphors"""
    
    # Base concepts that work for any brand
    base_concepts = [
        {
            "title": "Growth & Progress",
            "description": f"Visual metaphor showing {company_name}'s journey of growth and continuous improvement",
            "metaphor": "Ascending staircase, growing plant, or upward arrow with symbolic elements"
        },
        {
            "title": "Connection & Community", 
            "description": f"Illustration representing how {company_name} brings people together and builds relationships",
            "metaphor": "Connected nodes, people collaborating, or interlocking puzzle pieces"
        },
        {
            "title": "Innovation & Creativity",
            "description": f"Creative representation of {company_name}'s innovative approach and forward-thinking",
            "metaphor": "Lightbulb moment, gears turning ideas into reality, or abstract creative flow"
        },
        {
            "title": "Excellence & Quality",
            "description": f"Visual showcasing {company_name}'s commitment to high standards and quality delivery",
            "metaphor": "Diamond formation, precision tools, or award/achievement symbols"
        }
    ]
    
    # Industry-specific concepts
    industry_concepts = {
        "tea": [
            {
                "title": "Mindful Moments",
                "description": f"Peaceful tea ritual showing {company_name}'s calming, meditative experience",
                "metaphor": "Steam rising forming zen patterns, tea leaves dancing, serene environment"
            },
            {
                "title": "Customization Journey",
                "description": f"Visual story of personalizing the perfect cup with {company_name}",
                "metaphor": "Multiple tea elements combining into perfect blend, customization interface"
            }
        ],
        "technology": [
            {
                "title": "Digital Transformation",
                "description": f"Showing how {company_name} transforms complex processes into simple solutions",
                "metaphor": "Complex machinery simplifying into elegant solution, data flowing smoothly"
            },
            {
                "title": "Future Vision",
                "description": f"Forward-looking illustration of {company_name}'s technological advancement",
                "metaphor": "Telescope viewing future possibilities, roadmap to innovation"
            }
        ],
        "healthcare": [
            {
                "title": "Healing & Care",
                "description": f"Compassionate care and healing journey with {company_name}",
                "metaphor": "Protective hands, healing energy, journey from illness to wellness"
            }
        ],
        "education": [
            {
                "title": "Knowledge Building",
                "description": f"Learning journey and skill development with {company_name}",
                "metaphor": "Books transforming into tools, knowledge tree growing"
            }
        ]
    }
    
    # Combine base concepts with industry-specific ones
    concepts = base_concepts.copy()
    
    industry_lower = industry.lower()
    for key in industry_concepts:
        if key in industry_lower:
            concepts.extend(industry_concepts[key])
            break
    
    # Return requested number of concepts
    return concepts[:num_concepts]

def _define_illustration_rules(primary_color, illustration_style):
    """Step 4: Set the Rules - Define illustration guidelines"""
    
    # Convert hex to RGB
    primary_rgb = _hex_to_rgb(primary_color)
    
    rules = {
        "color_palette": {
            "primary": primary_color,
            "primary_rgb": primary_rgb,
            "usage": "Primary brand color for key elements and accents"
        },
        "style_guidelines": {
            "style": illustration_style,
            "background": "Clean, minimal, or transparent",
            "consistency": "Maintain same style across all illustrations"
        },
        "dos": [
            "Use consistent color palette",
            "Maintain clean, professional appearance",
            "Include metaphorical elements, not literal representations",
            "Ensure scalability for different sizes",
            "Keep brand personality in mind"
        ],
        "donts": [
            "Don't use overly complex details",
            "Don't mix different illustration styles",
            "Don't use colors outside the brand palette",
            "Don't create literal, obvious representations",
            "Don't include text in illustrations"
        ]
    }
    
    return rules

def _create_recraft_prompt(concept, style, rules, company_name):
    """Create optimized prompt for Recraft V3"""
    
    # Base prompt structure
    prompt = f"{concept['description']}. {concept['metaphor']}. "
    
    # Style instructions
    style_instructions = {
        "vector_illustration/thin": "Clean minimalist line art, thin strokes, simple geometric shapes",
        "digital_illustration/2d_art_poster": "Flat vector illustration, bright colors, modern poster style",
        "digital_illustration/hand_drawn": "Hand-drawn style with texture, authentic feel, organic lines",
        "vector_illustration/infographical": "Isometric technical illustration, clean diagrams, professional",
        "digital_illustration/expressionism": "Sophisticated artistic illustration, refined color palette"
    }
    
    prompt += style_instructions.get(style, "Professional modern illustration") + ". "
    
    # Add composition and quality instructions
    prompt += (
        "Professional composition, balanced layout, corporate quality. "
        "Clean background, suitable for business presentations. "
        "Abstract and metaphorical rather than literal. "
        "High-quality, scalable illustration style."
    )
    
    return prompt

def _remove_background_rembg(image_path):
    """Remove background using rembg"""
    try:
        from rembg import remove
        
        with open(image_path, 'rb') as input_file:
            input_data = input_file.read()
        
        output_data = remove(input_data)
        
        # Create transparent version filename
        transparent_path = image_path.replace('.png', '_transparent.png')
        with open(transparent_path, 'wb') as output_file:
            output_file.write(output_data)
        
        print(f"    ✅ Background removed: {transparent_path}")
        return transparent_path
        
    except ImportError:
        print("    ⚠️ rembg not available, skipping background removal")
        return None
    except Exception as e:
        print(f"    ❌ Background removal failed: {e}")
        return None

def _hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

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