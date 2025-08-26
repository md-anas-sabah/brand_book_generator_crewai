from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
import os
import re

class PPTXGenerator:
    """
    Assembles brand assets and literature into a PowerPoint brand book.
    """

    def _add_title_slide(self, prs, company_name):
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = f"{company_name} Brand Book"
        slide.placeholders[1].text = "A comprehensive guide to your brand identity"

    def _add_logo_slide(self, prs, logos):
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = "Logo Variations"
        left = Inches(1)
        top = Inches(1.5)
        width = Inches(2)
        for i, logo_path in enumerate(logos):
            if os.path.exists(logo_path):
                slide.shapes.add_picture(logo_path, left, top, width=width)
                left += width + Inches(0.3)

    def _add_palette_slide(self, prs, palette):
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = "Color Palette"
        left = Inches(1)
        top = Inches(1.5)
        width = Inches(1.5)
        height = Inches(1)
        spacing = Inches(0.3)
        for i, (color_name, hexcode) in enumerate(palette.items()):
            shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                left + i * (width + spacing),
                top,
                width,
                height
            )
            # Safe hex parsing - handle both strings and lists
            if isinstance(hexcode, list):
                hexcode = hexcode[0] if hexcode else "#CCCCCC"
            hexcode_clean = (hexcode or "#CCCCCC").lstrip("#")
            if len(hexcode_clean) == 3:
                hexcode_clean = ''.join([c*2 for c in hexcode_clean])
            if len(hexcode_clean) != 6:
                hexcode_clean = "CCCCCC"
            try:
                rgb = tuple(int(hexcode_clean[j:j+2], 16) for j in (0, 2, 4))
            except Exception:
                rgb = (204, 204, 204)
            fill = shape.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(*rgb)
            tf = shape.text_frame
            tf.text = f"{color_name.capitalize()}\n#{hexcode_clean.upper()}"
            for p in tf.paragraphs:
                p.font.size = Pt(12)
                p.font.bold = True

    def _add_typography_slide(self, prs, typography):
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = "Typography"
        left = Inches(1)
        top = Inches(1.5)
        width = Inches(6)
        height = Inches(2)
        textbox = slide.shapes.add_textbox(left, top, width, height)
        tf = textbox.text_frame
        tf.word_wrap = True
        tf.text = f"Primary Font: {typography.get('primary')}\nSecondary Font: {typography.get('secondary')}"
        for p in tf.paragraphs:
            p.font.size = Pt(18)

    def _add_brand_essence_slides(self, prs, brand_essence):
        """Add slides for brand essence and market analysis"""
        
        # Company Profile Slide
        if brand_essence.get("company_profile"):
            profile = brand_essence["company_profile"]
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = "Company Profile"
            content = f"""
Company: {profile.get('name', 'N/A')}
Industry: {profile.get('industry', 'N/A')}
Target Audience: {profile.get('target_audience', 'N/A')}

Core Values:
{chr(10).join(['• ' + value for value in profile.get('core_values', [])])}
            """.strip()
            slide.placeholders[1].text = content
        
        # Market Analysis Slide
        if brand_essence.get("market_analysis"):
            analysis = brand_essence["market_analysis"]
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = "Market Analysis & Insights"
            
            content_parts = []
            
            if analysis.get("industry_trends"):
                content_parts.append("Industry Trends:")
                content_parts.extend(['• ' + trend for trend in analysis["industry_trends"][:5]])
                content_parts.append("")
            
            if analysis.get("competitor_insights", {}).get("notable_competitors"):
                content_parts.append("Key Competitors:")
                competitors = analysis["competitor_insights"]["notable_competitors"][:6]
                content_parts.append(', '.join(competitors))
                content_parts.append("")
            
            if analysis.get("design_trends", {}).get("design_styles"):
                styles = analysis["design_trends"]["design_styles"][:4]
                content_parts.append(f"Popular Design Styles: {', '.join(styles)}")
            
            slide.placeholders[1].text = '\n'.join(content_parts)
        
        # Brand Positioning Slide
        if brand_essence.get("brand_positioning"):
            positioning = brand_essence["brand_positioning"]
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = "Brand Positioning"
            
            content = f"""
Unique Value Proposition:
{positioning.get('unique_value_proposition', 'N/A')}

Brand Promise:
{positioning.get('brand_promise', 'N/A')}

Brand Personality:
{', '.join(positioning.get('brand_personality', []))}

Competitive Advantage:
{positioning.get('competitive_advantage', 'N/A')}
            """.strip()
            slide.placeholders[1].text = content

    def _add_visual_style_slide(self, prs, visual_style, photography_style):
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = "Visual & Photography Guidelines"
        left = Inches(1)
        top = Inches(1.5)
        width = Inches(7)
        height = Inches(2.5)
        textbox = slide.shapes.add_textbox(left, top, width, height)
        tf = textbox.text_frame
        tf.word_wrap = True
        tf.text = f"Visual Style:\n{visual_style}\n\nPhotography Style:\n{photography_style}"
        for p in tf.paragraphs:
            p.font.size = Pt(16)

    def _add_story_and_mission(self, prs, story):
        # Attempt to split Brand Story, Mission, Values if text is present
        # Accepts either a dict (recommended) or a single string
        if isinstance(story, dict):
            if "Brand Story" in story:
                self._add_multislide_section(prs, "Brand Story", story["Brand Story"], 450)
            if "Mission Statement" in story:
                self._add_multislide_section(prs, "Mission Statement", story["Mission Statement"], 450)
            if "Our Values" in story:
                self._add_bullet_slide(prs, "Our Values", story["Our Values"])
        else:
            # Fallback: Single slide, split if too long
            self._add_multislide_section(prs, "Brand Story & Mission", story, 600)

    def _add_bullet_slide(self, prs, title, content):
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = title
        left, top, width, height = Inches(1), Inches(1.5), Inches(7), Inches(3)
        textbox = slide.shapes.add_textbox(left, top, width, height)
        tf = textbox.text_frame
        tf.word_wrap = True
        # Accepts either a list or a string with \n, commas, or numbered
        if isinstance(content, list):
            for item in content:
                p = tf.add_paragraph()
                p.text = item.strip()
                p.level = 0
                p.font.size = Pt(18)
        else:
            # Try to split numbered/bulleted/commas
            items = []
            lines = content.split("\n")
            for line in lines:
                if not line.strip():
                    continue
                # Numbered?
                m = re.match(r"^\d+\.\s*(.*)", line.strip())
                if m:
                    items.append(m.group(1))
                elif "," in line and len(line.split(",")) <= 8:
                    items.extend([i.strip() for i in line.split(",")])
                else:
                    items.append(line.strip())
            for item in items:
                p = tf.add_paragraph()
                p.text = item.strip()
                p.level = 0
                p.font.size = Pt(18)

    def _add_multislide_section(self, prs, title, content, max_chars=500):
        """Splits long text content into multiple slides if needed."""
        # Split at sentence boundaries if possible
        sentences = re.split(r'(?<=[.!?])\s+', content)
        chunks = []
        current = ""
        for s in sentences:
            if len(current) + len(s) < max_chars:
                current += " " + s
            else:
                if current:
                    chunks.append(current.strip())
                current = s
        if current:
            chunks.append(current.strip())
        for idx, chunk in enumerate(chunks):
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            slide.shapes.title.text = f"{title} ({idx+1})" if len(chunks) > 1 else title
            left, top, width, height = Inches(1), Inches(1.5), Inches(7), Inches(3)
            textbox = slide.shapes.add_textbox(left, top, width, height)
            tf = textbox.text_frame
            tf.word_wrap = True
            tf.text = chunk
            for p in tf.paragraphs:
                p.font.size = Pt(18 if len(chunk) < 300 else 16)

    def _add_voice_slide(self, prs, voice_tone):
        self._add_multislide_section(prs, "Brand Voice & Tone", voice_tone, max_chars=500)

    def _add_messaging_slide(self, prs, messaging_arch):
        # Try to split value propositions into bullets or slides
        lines = messaging_arch.split('\n')
        key_props = []
        for line in lines:
            m = re.match(r'^\d+\.\s*Key Value Proposition #[0-9]+: (.+)', line.strip())
            if m:
                key_props.append(m.group(1))
        if key_props:
            self._add_bullet_slide(prs, "Key Value Propositions", key_props)
        else:
            self._add_multislide_section(prs, "Messaging & Value Propositions", messaging_arch, max_chars=500)

    def _add_marketing_copy_slides(self, prs, marketing_copy):
        for channel, copy in marketing_copy.items():
            title = f"Marketing Copy: {channel.replace('_', ' ').title()}"
            self._add_multislide_section(prs, title, copy, max_chars=500)

    def _add_collateral_slide(self, prs, collaterals):
        # If it's a dict, bullet each
        if isinstance(collaterals, dict):
            for name, desc in collaterals.items():
                self._add_multislide_section(prs, f"Collateral: {name.replace('_',' ').title()}", desc, max_chars=500)
        else:
            self._add_multislide_section(prs, "Brand Collateral Templates", collaterals, max_chars=500)

    def create_pptx(self, company_name, identity_data, literature_data, brand_essence=None):
        prs = Presentation()

        # Title Slide
        self._add_title_slide(prs, company_name)
        
        # Brand Essence & Market Analysis (if available)
        if brand_essence:
            self._add_brand_essence_slides(prs, brand_essence)

        # Logo Variations
        self._add_logo_slide(prs, identity_data.get("logos", []))

        # Color Palette
        self._add_palette_slide(prs, identity_data.get("palette", {}))

        # Typography
        self._add_typography_slide(prs, identity_data.get("typography", {}))

        # Visual Style & Photography
        self._add_visual_style_slide(
            prs,
            identity_data.get("visual_style", ""),
            identity_data.get("photography_style", ""),
        )

        # Brand Story, Mission, Values (handled as dict if possible)
        story_data = literature_data.get("brand_story", "")
        # Try to split brand_story content into dict
        if isinstance(story_data, str) and "Mission Statement:" in story_data and "Our Values:" in story_data:
            bd = {}
            m1 = re.search(r"Brand Story:(.+?)Mission Statement:", story_data, re.DOTALL)
            m2 = re.search(r"Mission Statement:(.+?)Our Values:", story_data, re.DOTALL)
            m3 = re.search(r"Our Values:(.+)", story_data, re.DOTALL)
            if m1: bd["Brand Story"] = m1.group(1).strip()
            if m2: bd["Mission Statement"] = m2.group(1).strip()
            if m3: bd["Our Values"] = m3.group(1).strip()
            self._add_story_and_mission(prs, bd)
        else:
            self._add_story_and_mission(prs, story_data)

        # Voice & Tone
        self._add_voice_slide(prs, literature_data.get("voice_tone", ""))

        # Messaging
        self._add_messaging_slide(prs, literature_data.get("messaging_arch", ""))

        # Marketing Copy
        self._add_marketing_copy_slides(prs, literature_data.get("marketing_copy", {}))

        # Collateral
        self._add_collateral_slide(prs, literature_data.get("collaterals", {}))

        # Save file in company-specific folder
        base_name = company_name.lower().replace(' ', '_')
        company_output_dir = os.path.join("output", base_name)
        os.makedirs(company_output_dir, exist_ok=True)
        file_name = f"{base_name}_brand_book.pptx"
        file_path = os.path.join(company_output_dir, file_name)
        prs.save(file_path)
        print(f"Brand Book PPTX saved at: {file_path}")
        return file_path

# Example usage
if __name__ == "__main__":
    identity_data = {
        "logos": [],
        "palette": {"primary": "#222", "secondary": "#EEE", "accent": "#FEC556"},
        "typography": {"primary": "Montserrat", "secondary": "Lato"},
        "visual_style": "Modern, minimal, lots of whitespace, bold accent color.",
        "photography_style": "Clean, authentic, natural light, focus on diversity."
    }
    literature_data = {
        "brand_story": {
            "Brand Story": "Acme is here to innovate fintech for everyone.",
            "Mission Statement": "Make finance easy for all.",
            "Our Values": ["Innovation", "Customer Focus", "Integrity"]
        },
        "voice_tone": "Friendly, helpful, smart.",
        "messaging_arch": "1. Key Value Proposition #1: Fast\n2. Key Value Proposition #2: Secure",
        "marketing_copy": {"website": "Welcome to Acme!", "email": "Acme for your finance.", "social_media": "Finance made easy."},
        "collaterals": {"business_card": "Modern layout", "email_signature": "Professional details"}
    }
    generator = PPTXGenerator()
    generator.create_pptx("Acme Corp", identity_data, literature_data)
