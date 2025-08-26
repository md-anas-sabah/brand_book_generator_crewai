from tools.fal_image_tool import generate_logo_variations
from tools.branding_resources import get_color_palette, get_typography, get_moodboard_prompt, get_photography_guidelines

class IdentityAgent:
    """
    Handles brand identity asset creation:
    - Logo variations (via FAL)
    - Color palette (local logic or LLM)
    - Typography (local logic or LLM)
    - Visual style/moodboard (prompt or static)
    - Brand photography guidelines (prompt or static)
    """

    def create_identity(self, company_name, industry, values, audience, logo_style, brand_essence=None):
        # 1. Logo variations
        print(f"Generating logo variations for {company_name}...")
        logos = generate_logo_variations(company_name, industry, logo_style)
        
        # 2. Color palette (enhanced with brand essence insights)
        print(f"Generating color palette for {company_name}...")
        if brand_essence and brand_essence.get('visual_direction'):
            color_direction = brand_essence['visual_direction'].get('color_direction', [])
            palette = get_color_palette(industry, logo_style, color_hints=color_direction)
        else:
            palette = get_color_palette(industry, logo_style)
        
        # 3. Typography (enhanced with brand essence insights)
        print(f"Generating typography for {company_name}...")
        if brand_essence and brand_essence.get('visual_direction'):
            style_hint = brand_essence['visual_direction'].get('recommended_style', logo_style)
            typography = get_typography(industry, style_hint)
        else:
            typography = get_typography(industry, logo_style)
        
        # 4. Visual style / moodboard description
        print(f"Generating visual style guidelines for {company_name}...")
        visual_style = get_moodboard_prompt(company_name, industry, logo_style, values, audience)
        
        # 5. Brand photography style/guidelines
        print(f"Generating photography guidelines for {company_name}...")
        photography_style = get_photography_guidelines(company_name, industry, logo_style, values, audience)
        
        # Return a dictionary for downstream steps (PPT, etc)
        return {
            "logos": logos,
            "palette": palette,
            "typography": typography,
            "visual_style": visual_style,
            "photography_style": photography_style,
        }

# Example test usage
if __name__ == "__main__":
    agent = IdentityAgent()
    output = agent.create_identity(
        company_name="Acme Corp",
        industry="Fintech",
        values="Trust, Innovation, Simplicity",
        audience="Young professionals",
        logo_style="Minimalistic"
    )
    from pprint import pprint
    pprint(output)
