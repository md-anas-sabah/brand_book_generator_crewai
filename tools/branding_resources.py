# tools/branding_resources.py

def get_color_palette(industry, style, color_hints=None, logo_color=None):
    """Generate color palette with optional research-based hints and user-specified logo color"""
    
    # Dynamic palettes based on research hints
    if color_hints:
        hint_palette = _generate_palette_from_hints(color_hints, style, logo_color)
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
    
    # If user provided logo_color, use it as primary color
    if logo_color:
        normalized_logo_color = _normalize_color_input(logo_color)
        if normalized_logo_color:
            base_palette["primary"] = normalized_logo_color
    
    base_palette["supporting"] = ["#E5E7EB", "#6B7280"]
    base_palette["hex_codes"] = [base_palette["primary"], base_palette["secondary"], base_palette["accent"], "#E5E7EB", "#6B7280"]
    
    return base_palette

def _generate_palette_from_hints(color_hints, style, logo_color=None):
    """Generate dynamic palette from research-based color hints"""
    # Enhanced color map with multiple variations per color
    color_variations = {
        "blue": ["#2563EB", "#3B82F6", "#1D4ED8", "#1E40AF", "#0EA5E9"],
        "red": ["#DC2626", "#EF4444", "#F87171", "#BE185D", "#E11D48"],
        "green": ["#059669", "#10B981", "#34D399", "#047857", "#065F46"],
        "yellow": ["#F59E0B", "#FBBF24", "#FCD34D", "#D97706", "#B45309"],
        "purple": ["#7C3AED", "#8B5CF6", "#A855F7", "#6D28D9", "#5B21B6"],
        "pink": ["#EC4899", "#F472B6", "#FB7185", "#DB2777", "#BE185D"],
        "orange": ["#EA580C", "#F97316", "#FB923C", "#C2410C", "#9A3412"],
        "teal": ["#0891B2", "#06B6D4", "#22D3EE", "#0E7490", "#155E75"],
        "gray": ["#6B7280", "#4B5563", "#374151", "#1F2937", "#111827"],
        "grey": ["#6B7280", "#4B5563", "#374151", "#1F2937", "#111827"],
        "black": ["#1F2937", "#111827", "#0F172A", "#030712", "#000000"],
        "white": ["#F9FAFB", "#F3F4F6", "#E5E7EB", "#D1D5DB", "#FFFFFF"],
        "navy": ["#1E40AF", "#1D4ED8", "#2563EB", "#1E3A8A", "#172554"],
        "burgundy": ["#7F1D1D", "#991B1B", "#B91C1C", "#DC2626", "#EF4444"],
        "coral": ["#FB7185", "#F472B6", "#EC4899", "#DB2777", "#BE185D"],
        "mint": ["#6EE7B7", "#34D399", "#10B981", "#059669", "#047857"],
        "sage": ["#84CC16", "#65A30D", "#4D7C0F", "#365314", "#1A2E05"]
    }
    
    if not color_hints:
        return None
    
    import random
    
    # Shuffle color hints to avoid always picking the same first color
    shuffled_hints = color_hints.copy()
    random.shuffle(shuffled_hints)
    
    # Get dynamic color variations based on research
    def get_color_variation(color_name, position=0):
        variations = color_variations.get(color_name.lower(), color_variations["blue"])
        # Use position to get different shades (primary=darker, secondary=medium, accent=brighter)
        # Also add some randomization within the position range
        base_index = min(position, len(variations) - 1)
        # Add slight randomization (±1) within bounds
        index = max(0, min(len(variations) - 1, base_index + random.randint(-1, 1)))
        return variations[index]
    
    # Use logo_color as primary if provided, otherwise use shuffled hints
    if logo_color:
        normalized_logo_color = _normalize_color_input(logo_color)
        primary_color = normalized_logo_color if normalized_logo_color else get_color_variation(shuffled_hints[0], 0)
    else:
        primary_color = get_color_variation(shuffled_hints[0], 0)  # Darker shade
    
    secondary_color = get_color_variation(shuffled_hints[1] if len(shuffled_hints) > 1 else "gray", 2)  # Medium shade
    accent_color = get_color_variation(shuffled_hints[2] if len(shuffled_hints) > 2 else shuffled_hints[0], 1)  # Brighter shade
    
    # Generate supporting colors that complement the palette
    supporting_colors = [
        get_color_variation(color_hints[0], 3) if len(color_hints) > 0 else "#E5E7EB",
        get_color_variation(color_hints[1] if len(color_hints) > 1 else "gray", 4)
    ]
    
    return {
        "primary": primary_color,
        "secondary": secondary_color, 
        "accent": accent_color,
        "supporting": supporting_colors,
        "hex_codes": [primary_color, secondary_color, accent_color] + supporting_colors
    }

def get_typography(industry, style, brand_essence=None, font_research_data=None):
    """Generate dynamic typography recommendations based on research and trends"""
    
    # If we have comprehensive font research data, use it (preferred method)
    if font_research_data:
        return {
            "primary": font_research_data.get("primary_font", "Inter"),
            "secondary": font_research_data.get("secondary_font", "Source Sans Pro"), 
            "font_colors": font_research_data.get("font_colors", {
                "primary_text": "#1A1A1A",
                "secondary_text": "#4A4A4A", 
                "accent_text": "#0066CC",
                "light_text": "#6B6B6B",
                "white_text": "#FFFFFF"
            }),
            "hierarchy": [
                f"H1: {font_research_data.get('primary_font', 'Inter')} Bold 32px", 
                f"H2: {font_research_data.get('primary_font', 'Inter')} Medium 24px", 
                f"Body: {font_research_data.get('secondary_font', 'Source Sans Pro')} Regular 16px",
                f"Caption: {font_research_data.get('secondary_font', 'Source Sans Pro')} Regular 14px"
            ],
            "description": font_research_data.get("font_rationale", "Research-driven font selection"),
            "research_based": True
        }
    
    # Fallback to style-based selection if no research data available
    typography_styles = {
        "minimalist": [
            {"primary": "Inter", "secondary": "Lato", "desc": "Ultra-clean geometric pairing"},
            {"primary": "Montserrat", "secondary": "Source Sans Pro", "desc": "Modern geometric with high legibility"},
            {"primary": "Poppins", "secondary": "Inter", "desc": "Friendly geometric with technical precision"},
            {"primary": "Work Sans", "secondary": "IBM Plex Sans", "desc": "Contemporary minimalist pairing"}
        ],
        "modern": [
            {"primary": "Inter", "secondary": "IBM Plex Sans", "desc": "Tech-forward, highly legible"},
            {"primary": "DM Sans", "secondary": "Inter", "desc": "Contemporary with excellent readability"},
            {"primary": "Space Grotesk", "secondary": "Inter", "desc": "Distinctive modern character"},
            {"primary": "Plus Jakarta Sans", "secondary": "Inter", "desc": "Fresh, modern Indonesian-inspired"}
        ],
        "colorful": [
            {"primary": "Poppins", "secondary": "Nunito Sans", "desc": "Playful, friendly, and energetic"},
            {"primary": "Comfortaa", "secondary": "Nunito", "desc": "Rounded, warm, and approachable"},
            {"primary": "Quicksand", "secondary": "Lato", "desc": "Soft, friendly geometric"},
            {"primary": "Varela Round", "secondary": "Poppins", "desc": "Playful rounded sans-serif"}
        ],
        "elegant": [
            {"primary": "Playfair Display", "secondary": "Source Sans Pro", "desc": "Classic serif with modern sans"},
            {"primary": "Cormorant Garamond", "secondary": "Lato", "desc": "Refined serif with clean sans"},
            {"primary": "Crimson Text", "secondary": "Inter", "desc": "Sophisticated reading experience"},
            {"primary": "Libre Baskerville", "secondary": "Source Sans Pro", "desc": "Traditional elegance meets modernity"}
        ],
        "professional": [
            {"primary": "Roboto", "secondary": "Open Sans", "desc": "Google's reliable, versatile pairing"},
            {"primary": "IBM Plex Sans", "secondary": "Inter", "desc": "Corporate-grade typography system"},
            {"primary": "Source Sans Pro", "secondary": "Roboto", "desc": "Adobe's professional standard"},
            {"primary": "Fira Sans", "secondary": "Lato", "desc": "Mozilla's clean, professional choice"}
        ],
        "creative": [
            {"primary": "Space Grotesk", "secondary": "Inter", "desc": "Distinctive, creative edge"},
            {"primary": "Archivo", "secondary": "Work Sans", "desc": "Bold, statement-making"},
            {"primary": "Manrope", "secondary": "Inter", "desc": "Modern with creative flair"},
            {"primary": "DM Sans", "secondary": "Nunito Sans", "desc": "Fresh, contemporary creative"}
        ]
    }
    
    # Check if we have research-based insights
    research_typography = None
    if brand_essence and brand_essence.get('market_analysis', {}).get('design_trends', {}).get('typography_trends'):
        typography_trends = brand_essence['market_analysis']['design_trends']['typography_trends']
        research_typography = _select_typography_from_trends(typography_trends)
    
    # If we have research data, use it
    if research_typography:
        return research_typography
    
    # Otherwise use dynamic selection from style pools
    import random
    
    # Determine style category
    style_lower = style.lower()
    style_category = "professional"  # default
    
    for category in typography_styles.keys():
        if category in style_lower or style_lower in category:
            style_category = category
            break
    
    # Industry overrides
    industry_style_map = {
        "technology": "modern",
        "fintech": "professional", 
        "finance": "professional",
        "healthcare": "professional",
        "creative": "creative",
        "education": "modern",
        "retail": "colorful",
        "ecommerce": "colorful",
        "consulting": "elegant"
    }
    
    industry_category = industry_style_map.get(industry.lower())
    if industry_category and industry_category in typography_styles:
        style_category = industry_category
    
    # Randomly select from the appropriate category for variety
    selected_typography = random.choice(typography_styles[style_category])
    
    return {
        "primary": selected_typography["primary"],
        "secondary": selected_typography["secondary"],
        "hierarchy": [
            f"H1: {selected_typography['primary']} Bold 32px", 
            f"H2: {selected_typography['primary']} Medium 24px", 
            f"Body: {selected_typography['secondary']} Regular 16px"
        ],
        "description": selected_typography["desc"]
    }
    
def _select_typography_from_trends(typography_trends):
    """Select typography based on research trends"""
    
    # Map research trends to font selections
    trend_typography_map = {
        "serif": {"primary": "Playfair Display", "secondary": "Source Sans Pro", "desc": "Research-driven serif selection"},
        "sans-serif": {"primary": "Inter", "secondary": "IBM Plex Sans", "desc": "Research-driven sans-serif selection"},
        "modern": {"primary": "Space Grotesk", "secondary": "Inter", "desc": "Research-driven modern selection"},
        "classic": {"primary": "Libre Baskerville", "secondary": "Source Sans Pro", "desc": "Research-driven classic selection"},
        "bold": {"primary": "Archivo", "secondary": "Work Sans", "desc": "Research-driven bold selection"},
        "light": {"primary": "Work Sans", "secondary": "Inter", "desc": "Research-driven light selection"},
        "thin": {"primary": "Lato", "secondary": "Inter", "desc": "Research-driven thin selection"},
        "condensed": {"primary": "Roboto Condensed", "secondary": "Inter", "desc": "Research-driven condensed selection"}
    }
    
    # Find the first matching trend
    for trend in typography_trends:
        if trend.lower() in trend_typography_map:
            selected = trend_typography_map[trend.lower()]
            return {
                "primary": selected["primary"],
                "secondary": selected["secondary"],
                "hierarchy": [
                    f"H1: {selected['primary']} Bold 32px", 
                    f"H2: {selected['primary']} Medium 24px", 
                    f"Body: {selected['secondary']} Regular 16px"
                ],
                "description": selected["desc"]
            }
    
    return None

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

def _normalize_color_input(color_input):
    """Normalize various color input formats to hex"""
    if not color_input:
        return None
    
    color_input = color_input.strip()
    
    # If it's already a hex color
    if color_input.startswith('#') and len(color_input) == 7:
        return color_input
    
    # If it's hex without #
    if len(color_input) == 6 and all(c in '0123456789ABCDEFabcdef' for c in color_input):
        return '#' + color_input
    
    # If it's RGB format like "rgb(255, 255, 255)" or "255, 255, 255"
    import re
    rgb_match = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', color_input.lower())
    if rgb_match:
        r, g, b = map(int, rgb_match.groups())
        return f"#{r:02x}{g:02x}{b:02x}"
    
    # If it's comma-separated RGB like "255, 255, 255"
    rgb_parts = [x.strip() for x in color_input.split(',')]
    if len(rgb_parts) == 3:
        try:
            r, g, b = map(int, rgb_parts)
            if all(0 <= x <= 255 for x in [r, g, b]):
                return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError:
            pass
    
    # Color name mapping
    color_names = {
        'red': '#DC2626', 'blue': '#2563EB', 'green': '#059669', 'yellow': '#F59E0B',
        'purple': '#7C3AED', 'orange': '#EA580C', 'pink': '#EC4899', 'teal': '#0891B2',
        'gray': '#6B7280', 'grey': '#6B7280', 'black': '#1F2937', 'white': '#FFFFFF',
        'navy': '#1E40AF', 'burgundy': '#7F1D1D', 'coral': '#FB7185', 'mint': '#6EE7B7',
        'sage': '#84CC16', 'gold': '#D97706', 'silver': '#9CA3AF', 'brown': '#92400E'
    }
    
    if color_input.lower() in color_names:
        return color_names[color_input.lower()]
    
    print(f"⚠️ Could not normalize color input '{color_input}', using default")
    return None

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
