from PIL import Image, ImageDraw, ImageFont
import io
import os
from typing import Dict, List, Tuple
import requests
from urllib.parse import urlparse

class CollateralAgent:
    """
    Generates mockups and collateral templates automatically based on brand assets.
    Creates visual representations of how the brand should be applied across various mediums.
    """
    
    def __init__(self, company_name: str = None):
        if company_name:
            base_name = company_name.lower().replace(' ', '_')
            self.output_dir = os.path.join("output", base_name, "collateral")
        else:
            self.output_dir = "output/collateral"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Standard template sizes (width, height)
        self.template_sizes = {
            "business_card": (1050, 600),  # 3.5" x 2" at 300 DPI
            "letterhead": (2550, 3300),   # 8.5" x 11" at 300 DPI
            "social_square": (1080, 1080), # Instagram square
            "social_story": (1080, 1920),  # Instagram story
            "banner_web": (1200, 628),     # Facebook cover/web banner
            "presentation_slide": (1920, 1080), # 16:9 presentation
            "email_header": (600, 200),    # Email header
            "logo_lockup": (800, 400)      # Logo lockup variations
        }
    
    def create_collateral_suite(self, company_name: str, identity_data: Dict, 
                               literature_data: Dict, brand_essence: Dict = None) -> Dict:
        """
        Create a comprehensive suite of brand collateral templates
        """
        print(f"🎨 Generating collateral suite for {company_name}...")
        
        # Extract brand assets
        palette = identity_data.get("palette", {})
        typography = identity_data.get("typography", {})
        
        # Generate all collateral types
        collateral_files = {}
        
        try:
            # Business card design
            print("  Creating business card mockup...")
            business_card_path = self._create_business_card(company_name, palette, typography)
            collateral_files["business_card"] = business_card_path
            
            # Letterhead design
            print("  Creating letterhead template...")
            letterhead_path = self._create_letterhead(company_name, palette, typography)
            collateral_files["letterhead"] = letterhead_path
            
            # Social media templates
            print("  Creating social media templates...")
            social_templates = self._create_social_templates(company_name, palette, typography, literature_data)
            collateral_files.update(social_templates)
            
            # Presentation template
            print("  Creating presentation template...")
            presentation_path = self._create_presentation_template(company_name, palette, typography)
            collateral_files["presentation"] = presentation_path
            
            # Email signature template
            print("  Creating email signature template...")
            email_sig_path = self._create_email_signature(company_name, palette, typography)
            collateral_files["email_signature"] = email_sig_path
            
            # Logo lockup variations
            print("  Creating logo lockup variations...")
            lockup_path = self._create_logo_lockups(company_name, palette, typography)
            collateral_files["logo_lockups"] = lockup_path
            
        except Exception as e:
            print(f"  Warning: Error creating some collateral: {e}")
        
        # Generate usage guidelines
        usage_guidelines = self._create_usage_guidelines(company_name, identity_data)
        
        return {
            "collateral_files": collateral_files,
            "usage_guidelines": usage_guidelines,
            "template_specifications": self._get_template_specs(),
            "file_formats": ["PNG", "SVG", "PDF"],
            "print_ready": True
        }
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return (51, 51, 51)  # Default gray
    
    def _create_business_card(self, company_name: str, palette: Dict, typography: Dict) -> str:
        """Create business card mockup"""
        width, height = self.template_sizes["business_card"]
        
        # Create image
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Get colors
        primary_color = self._hex_to_rgb(palette.get("primary", "#333333"))
        accent_color = self._hex_to_rgb(palette.get("accent", "#0066CC"))
        
        # Background accent
        draw.rectangle([0, 0, width//4, height], fill=accent_color)
        
        # Company name (larger font simulation)
        company_y = height // 4
        draw.text((width//4 + 40, company_y), company_name, fill=primary_color)
        
        # Contact info placeholders
        info_y = company_y + 80
        contact_info = [
            "John Doe, CEO",
            "john@company.com",
            "+1 (555) 123-4567",
            "www.company.com"
        ]
        
        for i, info in enumerate(contact_info):
            draw.text((width//4 + 40, info_y + i*40), info, fill=primary_color)
        
        # Save
        filename = f"{company_name.lower().replace(' ', '_')}_business_card.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, 'PNG', quality=95)
        
        return filepath
    
    def _create_letterhead(self, company_name: str, palette: Dict, typography: Dict) -> str:
        """Create letterhead template"""
        width, height = self.template_sizes["letterhead"]
        
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Get colors
        primary_color = self._hex_to_rgb(palette.get("primary", "#333333"))
        accent_color = self._hex_to_rgb(palette.get("accent", "#0066CC"))
        
        # Header section with accent
        header_height = height // 8
        draw.rectangle([0, 0, width, header_height], fill=accent_color)
        
        # Company name in header
        draw.text((80, header_height//3), company_name, fill=(255, 255, 255))
        
        # Footer with contact info
        footer_y = height - header_height
        draw.rectangle([0, footer_y, width, height], fill=primary_color)
        
        # Contact details in footer
        contact_text = f"{company_name} | 123 Business St, City, State 12345 | contact@{company_name.lower().replace(' ', '')}.com"
        draw.text((80, footer_y + 30), contact_text, fill=(255, 255, 255))
        
        # Save
        filename = f"{company_name.lower().replace(' ', '_')}_letterhead.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, 'PNG', quality=95)
        
        return filepath
    
    def _create_social_templates(self, company_name: str, palette: Dict, 
                                typography: Dict, literature_data: Dict) -> Dict:
        """Create social media templates"""
        templates = {}
        
        # Square post template
        width, height = self.template_sizes["social_square"]
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        primary_color = self._hex_to_rgb(palette.get("primary", "#333333"))
        accent_color = self._hex_to_rgb(palette.get("accent", "#0066CC"))
        
        # Gradient background simulation
        for y in range(height):
            color_ratio = y / height
            r = int(accent_color[0] * (1 - color_ratio) + primary_color[0] * color_ratio)
            g = int(accent_color[1] * (1 - color_ratio) + primary_color[1] * color_ratio)
            b = int(accent_color[2] * (1 - color_ratio) + primary_color[2] * color_ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Company name overlay
        draw.text((width//4, height//2), company_name, fill=(255, 255, 255))
        
        # Sample tagline
        tagline = "Innovating Your Future"
        if literature_data.get("messaging_arch"):
            tagline = str(literature_data["messaging_arch"])[:30] + "..."
        
        draw.text((width//4, height//2 + 100), tagline, fill=(255, 255, 255))
        
        filename = f"{company_name.lower().replace(' ', '_')}_social_square.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, 'PNG', quality=95)
        templates["social_square"] = filepath
        
        # Story template (simplified version)
        story_width, story_height = self.template_sizes["social_story"]
        story_img = Image.new('RGB', (story_width, story_height), color=accent_color)
        story_draw = ImageDraw.Draw(story_img)
        
        # Center company name
        story_draw.text((story_width//4, story_height//2), company_name, fill=(255, 255, 255))
        
        story_filename = f"{company_name.lower().replace(' ', '_')}_social_story.png"
        story_filepath = os.path.join(self.output_dir, story_filename)
        story_img.save(story_filepath, 'PNG', quality=95)
        templates["social_story"] = story_filepath
        
        return templates
    
    def _create_presentation_template(self, company_name: str, palette: Dict, typography: Dict) -> str:
        """Create presentation slide template"""
        width, height = self.template_sizes["presentation_slide"]
        
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        primary_color = self._hex_to_rgb(palette.get("primary", "#333333"))
        accent_color = self._hex_to_rgb(palette.get("accent", "#0066CC"))
        
        # Top accent bar
        draw.rectangle([0, 0, width, 100], fill=accent_color)
        
        # Company name in corner
        draw.text((50, 30), company_name, fill=(255, 255, 255))
        
        # Title area
        draw.text((100, height//3), "Presentation Title", fill=primary_color)
        
        # Content area placeholder
        draw.rectangle([100, height//2, width-100, height-100], outline=primary_color, width=3)
        draw.text((120, height//2 + 50), "Content Area", fill=primary_color)
        
        # Save
        filename = f"{company_name.lower().replace(' ', '_')}_presentation_template.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, 'PNG', quality=95)
        
        return filepath
    
    def _create_email_signature(self, company_name: str, palette: Dict, typography: Dict) -> str:
        """Create email signature template"""
        width, height = self.template_sizes["email_header"]
        
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        primary_color = self._hex_to_rgb(palette.get("primary", "#333333"))
        accent_color = self._hex_to_rgb(palette.get("accent", "#0066CC"))
        
        # Left accent bar
        draw.rectangle([0, 0, 10, height], fill=accent_color)
        
        # Name and title
        draw.text((30, 20), "John Doe", fill=primary_color)
        draw.text((30, 50), "CEO", fill=primary_color)
        draw.text((30, 80), company_name, fill=accent_color)
        
        # Contact info
        draw.text((30, 120), "john@company.com | +1 (555) 123-4567", fill=primary_color)
        
        # Save
        filename = f"{company_name.lower().replace(' ', '_')}_email_signature.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, 'PNG', quality=95)
        
        return filepath
    
    def _create_logo_lockups(self, company_name: str, palette: Dict, typography: Dict) -> str:
        """Create logo lockup variations"""
        width, height = self.template_sizes["logo_lockup"]
        
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        primary_color = self._hex_to_rgb(palette.get("primary", "#333333"))
        
        # Main logo area (placeholder)
        logo_size = 100
        logo_x = width // 4
        logo_y = height // 4
        
        # Logo placeholder
        draw.rectangle([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size], 
                      outline=primary_color, width=3)
        draw.text((logo_x + 20, logo_y + 40), "LOGO", fill=primary_color)
        
        # Company name beside logo
        draw.text((logo_x + logo_size + 30, logo_y + 30), company_name, fill=primary_color)
        
        # Tagline below
        draw.text((logo_x + logo_size + 30, logo_y + 70), "Your Tagline Here", fill=primary_color)
        
        # Save
        filename = f"{company_name.lower().replace(' ', '_')}_logo_lockups.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, 'PNG', quality=95)
        
        return filepath
    
    def _create_usage_guidelines(self, company_name: str, identity_data: Dict) -> Dict:
        """Create comprehensive usage guidelines"""
        palette = identity_data.get("palette", {})
        typography = identity_data.get("typography", {})
        
        guidelines = {
            "logo_usage": {
                "minimum_size": "1 inch width for print, 72px for digital",
                "clear_space": "Minimum clear space = 1/2 height of logo on all sides",
                "backgrounds": "Use on white, light colors, or brand colors only",
                "donts": [
                    "Don't stretch or distort the logo",
                    "Don't use on busy backgrounds",
                    "Don't change colors without approval",
                    "Don't add effects or shadows"
                ]
            },
            "color_usage": {
                "primary_applications": "Headers, buttons, key elements",
                "secondary_applications": "Backgrounds, large areas",
                "accent_applications": "CTAs, highlights, links",
                "accessibility": "Ensure minimum 4.5:1 contrast ratio for text",
                "print_specifications": "Always use CMYK values for print production"
            },
            "typography_hierarchy": {
                "h1_usage": "Page titles, hero headings",
                "h2_usage": "Section headings, subsections", 
                "body_usage": "Paragraphs, general content",
                "minimum_sizes": "12pt for print body text, 16px for digital"
            },
            "spacing_guidelines": {
                "margin_standards": "Consistent margins across all materials",
                "element_spacing": "Use multiples of 8px for digital spacing",
                "print_bleeds": "Include 0.125\" bleed for print materials"
            }
        }
        
        return guidelines
    
    def _get_template_specs(self) -> Dict:
        """Get technical specifications for all templates"""
        return {
            "business_card": {
                "dimensions": "3.5\" x 2\"",
                "resolution": "300 DPI",
                "format": "CMYK for print, RGB for digital",
                "bleed": "0.125\" all sides"
            },
            "letterhead": {
                "dimensions": "8.5\" x 11\"", 
                "resolution": "300 DPI",
                "format": "CMYK for print",
                "margins": "0.5\" minimum"
            },
            "social_media": {
                "square_post": "1080x1080px, RGB, 72 DPI",
                "story": "1080x1920px, RGB, 72 DPI",
                "banner": "1200x628px, RGB, 72 DPI"
            },
            "presentation": {
                "dimensions": "1920x1080px (16:9)",
                "resolution": "96 DPI",
                "format": "RGB"
            }
        }