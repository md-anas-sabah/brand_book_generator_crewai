# tools/branding_resources.py

def get_color_palette(industry, style, color_hints=None):
    """Generate color palette with optional research-based hints"""
    
    # Dynamic palettes based on research hints
    if color_hints:
        hint_palette = _generate_palette_from_hints(color_hints, style)
        if hint_palette:
            return hint_palette
    
    # Existing logic as fallback
    if style.lower() == "minimalistic":
        return {
            "primary": "#0A0A0A", 
            "secondary": "#F2F2F2", 
            "accent": "#FFAD05",
            "supporting": ["#E0E0E0", "#666666"],
            "hex_codes": ["#0A0A0A", "#F2F2F2", "#FFAD05", "#E0E0E0", "#666666"]
        }
    if style.lower() in ["colourful", "colorful"]:
        return {
            "primary": "#4285F4", 
            "secondary": "#EA4335", 
            "accent": "#FBBC05",
            "supporting": ["#34A853", "#9C27B0"],
            "hex_codes": ["#4285F4", "#EA4335", "#FBBC05", "#34A853", "#9C27B0"]
        }
    
    # Industry-specific palettes
    industry_palettes = {
        "tech": {"primary": "#2563EB", "secondary": "#1E293B", "accent": "#06B6D4"},
        "finance": {"primary": "#1F2937", "secondary": "#3B82F6", "accent": "#059669"},
        "healthcare": {"primary": "#DC2626", "secondary": "#1F2937", "accent": "#059669"},
        "education": {"primary": "#7C3AED", "secondary": "#1F2937", "accent": "#F59E0B"},
        "retail": {"primary": "#EC4899", "secondary": "#1F2937", "accent": "#10B981"}
    }
    
    base_palette = industry_palettes.get(industry.lower(), {"primary": "#333", "secondary": "#BBB", "accent": "#00B894"})
    base_palette["supporting"] = ["#E5E7EB", "#6B7280"]
    base_palette["hex_codes"] = [base_palette["primary"], base_palette["secondary"], base_palette["accent"], "#E5E7EB", "#6B7280"]
    
    return base_palette

def _generate_palette_from_hints(color_hints, style):
    """Generate palette from research-based color hints"""
    color_map = {
        "blue": "#2563EB", "red": "#DC2626", "green": "#059669", "yellow": "#F59E0B",
        "purple": "#7C3AED", "pink": "#EC4899", "orange": "#EA580C", "teal": "#0891B2",
        "gray": "#6B7280", "black": "#1F2937", "white": "#F9FAFB"
    }
    
    if not color_hints:
        return None
    
    primary_color = color_map.get(color_hints[0].lower(), "#333333")
    secondary_color = color_map.get(color_hints[1].lower() if len(color_hints) > 1 else "gray", "#6B7280")
    accent_color = color_map.get(color_hints[2].lower() if len(color_hints) > 2 else "blue", "#2563EB")
    
    return {
        "primary": primary_color,
        "secondary": secondary_color, 
        "accent": accent_color,
        "supporting": ["#E5E7EB", "#9CA3AF"],
        "hex_codes": [primary_color, secondary_color, accent_color, "#E5E7EB", "#9CA3AF"]
    }

def get_typography(industry, style):
    """Generate typography recommendations with enhanced options"""
    
    style_typography = {
        "minimalistic": {
            "primary": "Montserrat", 
            "secondary": "Lato",
            "hierarchy": ["H1: Montserrat Bold 32px", "H2: Montserrat Medium 24px", "Body: Lato Regular 16px"],
            "description": "Clean, geometric sans-serif pairing for modern minimalist brands"
        },
        "colourful": {
            "primary": "Poppins", 
            "secondary": "Raleway",
            "hierarchy": ["H1: Poppins Bold 36px", "H2: Poppins Medium 26px", "Body: Raleway Regular 16px"],
            "description": "Friendly, approachable fonts perfect for vibrant, energetic brands"
        },
        "modern": {
            "primary": "Inter", 
            "secondary": "Source Sans Pro",
            "hierarchy": ["H1: Inter Bold 34px", "H2: Inter Medium 25px", "Body: Source Sans Pro Regular 16px"],
            "description": "Contemporary, highly legible fonts optimized for digital interfaces"
        },
        "elegant": {
            "primary": "Playfair Display", 
            "secondary": "Source Sans Pro",
            "hierarchy": ["H1: Playfair Display Bold 36px", "H2: Playfair Display Medium 26px", "Body: Source Sans Pro Regular 16px"],
            "description": "Sophisticated serif and sans-serif combination for premium brands"
        },
        "professional": {
            "primary": "Roboto", 
            "secondary": "Open Sans",
            "hierarchy": ["H1: Roboto Bold 32px", "H2: Roboto Medium 24px", "Body: Open Sans Regular 16px"],
            "description": "Reliable, versatile fonts suitable for corporate and business applications"
        }
    }
    
    # Industry-specific recommendations
    industry_typography = {
        "tech": "modern",
        "finance": "professional", 
        "healthcare": "professional",
        "education": "modern",
        "retail": "colourful",
        "consulting": "elegant",
        "creative": "colourful"
    }
    
    # Determine style
    final_style = style.lower()
    if final_style not in style_typography:
        final_style = industry_typography.get(industry.lower(), "professional")
    
    return style_typography.get(final_style, style_typography["professional"])

def get_moodboard_prompt(company_name, industry, logo_style, values, audience):
    return (
        f"Visual style for {company_name} in {industry}: "
        f"{logo_style} aesthetic, values: {values}, audience: {audience}. "
        f"Use whitespace, on-brand accent color, modern design cues."
    )

def get_photography_guidelines(company_name, industry, logo_style, values, audience):
    return (
        f"Photography style for {company_name}: {logo_style} and {industry} feel. "
        f"Show diversity, authenticity, and lighting that supports brand values: {values}. "
        f"Images should resonate with {audience}."
    )


# tools/branding_resources.py

def get_brand_story_prompt(company, industry, values, audience):
    return (
        f"Write a compelling brand story and mission statement for a company called '{company}' in the {industry} sector. "
        f"The brand values are: {values}. The target audience is: {audience}. "
        f"Focus on emotional connection, purpose, and vision."
    )

def get_voice_tone_prompt(company, industry, values, audience):
    return (
        f"Describe the brand voice and tone for '{company}' ({industry}), "
        f"based on the values: {values}, for an audience of {audience}. "
        "Specify if it should be friendly, authoritative, playful, etc."
    )

def get_messaging_prompt(company, industry, values, audience):
    return (
        f"Outline the messaging architecture for '{company}' in {industry}. "
        f"List 3-5 key value propositions tailored to {audience}. "
        "Each should be 1-2 sentences max, actionable and distinct."
    )

def get_marketing_copy_prompts(company, industry, values, audience):
    return {
        "website": (
            f"Write a homepage headline and subheadline for '{company}' in {industry}, "
            f"emphasizing values: {values} for {audience}."
        ),
        "email": (
            f"Write a promotional email subject and preview text for '{company}', "
            f"highlighting {values} to {audience}."
        ),
        "social_media": (
            f"Write a catchy social media post for '{company}' ({industry}), "
            f"to engage {audience} using the brand's values: {values}."
        ),
        "ad_copy": (
            f"Write a short, punchy ad copy for '{company}' in {industry}, "
            f"with a call-to-action relevant to {audience}."
        ),
    }

def get_collateral_templates(company, industry, values, audience):
    return {
        "business_card": f"Simple, clean business card layout for {company} in {industry}. Emphasize clarity, logo, and minimal info.",
        "letterhead": f"Letterhead with {company} branding, address, and subtle color accent from brand palette.",
        "email_signature": f"Professional email signature for {company} with logo, name, title, and key contact details.",
        "presentation_template": f"PPT cover slide and content slide layouts using {company} palette and fonts.",
        "social_templates": f"Instagram/Facebook post and story templates reflecting {company}'s style and values."
    }
