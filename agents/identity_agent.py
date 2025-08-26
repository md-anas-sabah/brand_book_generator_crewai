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

    def create_identity(self, company_name, industry, values, audience, logo_style):
        # 1. Logo variations
        print(f"Generating logo variations for {company_name}...")
        logos = generate_logo_variations(company_name, industry, logo_style)
        
        # 2. Color palette
        print(f"Generating color palette for {company_name}...")
        palette = get_color_palette(industry, logo_style)
        
        # 3. Typography
        print(f"Generating typography for {company_name}...")
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
