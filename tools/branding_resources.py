# tools/branding_resources.py

def get_color_palette(industry, style):
    if style.lower() == "minimalistic":
        return {"primary": "#0A0A0A", "secondary": "#F2F2F2", "accent": "#FFAD05"}
    if style.lower() == "colourful":
        return {"primary": "#4285F4", "secondary": "#EA4335", "accent": "#FBBC05"}
    return {"primary": "#333", "secondary": "#BBB", "accent": "#00B894"}

def get_typography(industry, style):
    if style.lower() == "minimalistic":
        return {"primary": "Montserrat", "secondary": "Lato"}
    if style.lower() == "colourful":
        return {"primary": "Poppins", "secondary": "Raleway"}
    return {"primary": "Roboto", "secondary": "Open Sans"}

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
