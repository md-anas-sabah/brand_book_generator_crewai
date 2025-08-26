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
                # Create detailed prompt for logo generation
                prompt = (
                    f"Professional logo design for {company_name}, {industry} industry. "
                    f"Style: {style}. Clean, modern, minimalistic design. "
                    f"Black background, high-resolution, corporate branding, "
                    f"vector-style illustration, simple and memorable design, logo on black background"
                )
                
                # Submit request to Ideogram V2A (matching first code pattern)
                result = fal.run(
                    "fal-ai/ideogram/v2a",
                    arguments={
                        "prompt": prompt,
                        "aspect_ratio": "1:1",  # Square format for logos
                        "style": "auto"
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
                    f"Black background, high-resolution, corporate branding, "
                    f"vector-style illustration, simple and memorable design, logo on black background"
                )
                
                result = fal.run(
                    "fal-ai/ideogram/v2a",
                    arguments={
                        "prompt": prompt,
                        "aspect_ratio": "1:1",
                        "style": "auto"
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