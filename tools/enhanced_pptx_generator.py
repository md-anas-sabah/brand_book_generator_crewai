from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN
from pptx.enum.text import MSO_ANCHOR
import os
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.font_research_agent import FontResearchAgent
from agents.introduction_content_agent import IntroductionContentAgent
from agents.brand_purpose_content_agent import BrandPurposeContentAgent
from agents.brand_story_content_agent import BrandStoryContentAgent


class GridLayout:
    """Grid-based layout system for consistent positioning"""
    
    def __init__(self, slide_width=Inches(10), slide_height=Inches(7.5), 
                 cols=12, rows=8, margin=Inches(0.5)):
        self.width = slide_width
        self.height = slide_height
        self.cols = cols
        self.rows = rows
        self.margin = margin
        
        # Calculate grid dimensions
        self.col_width = (slide_width - 2 * margin) / cols
        self.row_height = (slide_height - 2 * margin) / rows
    
    def get_position(self, col, row, width_cols=1, height_rows=1):
        """Get position and size for grid cell"""
        left = self.margin + (col * self.col_width)
        top = self.margin + (row * self.row_height)
        width = width_cols * self.col_width
        height = height_rows * self.row_height
        return left, top, width, height


class TextStyler:
    """Reusable text styling system"""
    
    def __init__(self, primary_font="Inter", secondary_font="Source Sans Pro", 
                 primary_color="#2E86AB", text_color="#FFFFFF"):
        self.primary_font = primary_font
        self.secondary_font = secondary_font
        self.primary_color = primary_color
        self.text_color = text_color
    
    def apply_title_style(self, paragraph, color=None, size=32):
        """Large, bold titles using primary font with color support"""
        paragraph.font.name = self.primary_font
        paragraph.font.size = Pt(size)
        paragraph.font.bold = True
        
        if color == 'white':
            paragraph.font.color.rgb = RGBColor(255, 255, 255)
        elif color == 'black':
            paragraph.font.color.rgb = RGBColor(0, 0, 0)
        elif isinstance(color, str) and color.startswith('#'):
            # Handle hex colors
            hex_color = color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            paragraph.font.color.rgb = RGBColor(r, g, b)
        else:
            paragraph.font.color.rgb = RGBColor(*self._hex_to_rgb(color or self.text_color))
    
    def apply_subtitle_style(self, paragraph, color=None, size=24):
        """Medium subtitles using secondary font with color support"""
        paragraph.font.name = self.secondary_font
        paragraph.font.size = Pt(size)
        paragraph.font.bold = False
        
        if color == 'white':
            paragraph.font.color.rgb = RGBColor(255, 255, 255)
        elif color == 'black':
            paragraph.font.color.rgb = RGBColor(0, 0, 0)
        elif isinstance(color, str) and color.startswith('#'):
            # Handle hex colors
            hex_color = color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            paragraph.font.color.rgb = RGBColor(r, g, b)
        else:
            paragraph.font.color.rgb = RGBColor(*self._hex_to_rgb(color or self.text_color))
    
    def apply_body_style(self, paragraph, color=None, size=16):
        """Body text using secondary font with color support"""
        paragraph.font.name = self.secondary_font
        paragraph.font.size = Pt(size)
        paragraph.font.bold = False
        
        if color == 'white':
            paragraph.font.color.rgb = RGBColor(255, 255, 255)
        elif color == 'black':
            paragraph.font.color.rgb = RGBColor(0, 0, 0)
        elif isinstance(color, str) and color.startswith('#'):
            # Handle hex colors like '#CCCCCC'
            hex_color = color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            paragraph.font.color.rgb = RGBColor(r, g, b)
        elif isinstance(color, RGBColor):
            # Handle RGBColor objects
            paragraph.font.color.rgb = color
        else:
            paragraph.font.color.rgb = RGBColor(*self._hex_to_rgb(color or self.text_color))
    
    def apply_caption_style(self, paragraph, color=None, size=12):
        """Small caption text"""
        paragraph.font.name = self.secondary_font
        paragraph.font.size = Pt(size)
        paragraph.font.bold = False
        paragraph.font.color.rgb = RGBColor(*self._hex_to_rgb(color or self.text_color))
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return (255, 255, 255)  # Default white


class EnhancedPPTXGenerator:
    """
    Enhanced PowerPoint Brand Book Generator with professional layout and styling
    """
    
    def __init__(self):
        self.font_research_agent = FontResearchAgent()
        self.introduction_agent = IntroductionContentAgent()
        self.brand_purpose_agent = BrandPurposeContentAgent()
        self.brand_story_agent = BrandStoryContentAgent()
        self.researched_fonts = None
        self.grid = GridLayout()
        self.styler = None
    
    def _initialize_styling(self, identity_data, company_name=""):
        """Initialize styling system based on brand data"""
        # Get fonts from research
        primary_font = self.researched_fonts['primary_font'] if self.researched_fonts else "Inter"
        secondary_font = self.researched_fonts['secondary_font'] if self.researched_fonts else "Source Sans Pro"
        
        # Get colors from brand palette
        palette = identity_data.get("palette", {}) if identity_data else {}
        primary_color = self._get_brand_color(palette, "primary", "#2E86AB")
        text_color = self._get_accessible_text_color(palette)
        
        self.styler = TextStyler(primary_font, secondary_font, primary_color, text_color)
        
        # Store company name for footers
        self.company_name = company_name
        self.slide_counter = 0
    
    def _get_brand_color(self, palette, color_name, default):
        """Extract color from palette safely"""
        if not palette:
            return default
        color = palette.get(color_name, default)
        if isinstance(color, list):
            return color[0] if color else default
        return color if color else default
    
    def _get_accessible_text_color(self, palette):
        """Get text color with good contrast against dark backgrounds"""
        primary_color = self._get_brand_color(palette, "primary", "#FFFFFF")
        
        try:
            # Calculate brightness
            hex_color = primary_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16) 
            b = int(hex_color[4:6], 16)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            
            # Use brand color if bright enough, otherwise white
            return primary_color if brightness > 100 else "#FFFFFF"
        except (ValueError, IndexError):
            return "#FFFFFF"
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return (255, 255, 255)
    
    def _add_slide_background(self, slide, gradient=False, identity_data=None, bg_color=None):
        """Add background to slide with optional pitch black background"""
        if bg_color == 'pitch_black' or bg_color == 'black':
            # Set solid pitch black background
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(0, 0, 0)  # Pure pitch black
        elif gradient and identity_data and identity_data.get("palette"):
            # Create gradient background
            bg_shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                0, 0, 
                Inches(10), Inches(7.5)
            )
            palette = identity_data["palette"]
            primary = self._get_brand_color(palette, "primary", "#1a1a1a")
            secondary = self._get_brand_color(palette, "secondary", "#2d2d2d")
            
            fill = bg_shape.fill
            fill.gradient()
            fill.gradient_angle = 135
            gradient = fill.gradient_stops
            gradient[0].color.rgb = RGBColor(*self._hex_to_rgb(primary))
            gradient[1].color.rgb = RGBColor(*self._hex_to_rgb(secondary))
            bg_shape.line.fill.background()
            
            # Move to back
            bg_shape.element.getparent().remove(bg_shape.element)
            slide.shapes._spTree.insert(1, bg_shape.element)
        else:
            # Solid dark background
            bg_shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                0, 0, 
                Inches(10), Inches(7.5)
            )
            bg_shape.fill.solid()
            bg_shape.fill.fore_color.rgb = RGBColor(26, 26, 26)
            bg_shape.line.fill.background()
            
            # Move to back
            bg_shape.element.getparent().remove(bg_shape.element)
            slide.shapes._spTree.insert(1, bg_shape.element)
    
    def _add_footer(self, slide, slide_number):
        """Add consistent footer with company name and slide number"""
        if not hasattr(self, 'company_name'):
            return
        
        left, top, width, height = self.grid.get_position(0, 7, 12, 1)
        
        # Company name on left
        company_textbox = slide.shapes.add_textbox(left, top, width / 2, height)
        company_frame = company_textbox.text_frame
        company_frame.text = self.company_name
        self.styler.apply_caption_style(company_frame.paragraphs[0], size=10)
        company_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
        
        # Slide number on right
        number_textbox = slide.shapes.add_textbox(left + width / 2, top, width / 2, height)
        number_frame = number_textbox.text_frame
        number_frame.text = str(slide_number)
        self.styler.apply_caption_style(number_frame.paragraphs[0], size=10)
        number_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
    
    def _add_logo_to_slide(self, slide, identity_data, col=10, row=0, size=1, opacity=1.0):
        """Add company logo at specified grid position with optional opacity"""
        if not identity_data or not identity_data.get("logos"):
            return
        
        logos = identity_data["logos"]
        logo_path = None
        
        for logo in logos:
            if isinstance(logo, str) and os.path.exists(logo):
                logo_path = logo
                break
        
        if logo_path:
            try:
                left, top, width, height = self.grid.get_position(col, row, size, size)
                logo = slide.shapes.add_picture(logo_path, left, top, width=width, height=height)
                
                # Set logo opacity if specified
                if opacity < 1.0:
                    try:
                        # Access the picture's transparency property
                        logo.element.get_or_add_alpha().val = int(opacity * 100000)  # Alpha in EMU units
                    except Exception as opacity_error:
                        print(f"Could not set logo opacity: {opacity_error}")
                        
            except Exception as e:
                print(f"Could not add logo: {e}")
    
    def _add_geometric_accent(self, slide, identity_data, dark_theme=False):
        """Add subtle geometric accent shape with dark theme support"""
        if not identity_data or not identity_data.get("palette"):
            return
        
        palette = identity_data["palette"]
        
        if dark_theme:
            # Use lighter colors for dark background
            accent_color = self._get_brand_color(palette, "accent", "#FFFFFF")
        else:
            accent_color = self._get_brand_color(palette, "accent", 
                                               self._get_brand_color(palette, "secondary", "#4A90E2"))
        
        # Add accent circle
        left, top, width, height = self.grid.get_position(9, 1, 2, 2)
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, width, height)
        circle.fill.solid()
        circle.fill.fore_color.rgb = RGBColor(*self._hex_to_rgb(accent_color))
        circle.fill.transparency = 0.7
        circle.line.fill.background()
    
    def _add_logo_as_background(self, slide, identity_data, opacity=0.85):
        """Add logo as full background with specified opacity"""
        if not identity_data or not identity_data.get("logos"):
            return
        
        try:
            # Get the first logo
            logo_path = identity_data["logos"][0]
            
            # Add logo covering the entire slide (10 inches x 7.5 inches standard)
            left = Inches(0)
            top = Inches(0) 
            width = Inches(10)
            height = Inches(7.5)
            
            # Add the logo image
            logo_shape = slide.shapes.add_picture(logo_path, left, top, width=width, height=height)
            
            # Set opacity (transparency)
            try:
                # Method 1: Try to set transparency via fill
                if hasattr(logo_shape, 'fill'):
                    logo_shape.fill.transparency = 1.0 - opacity  # transparency is inverse of opacity
                
                # Method 2: Alternative method for transparency
                elif hasattr(logo_shape, 'element'):
                    # This sets the alpha channel for transparency
                    alpha_value = int(opacity * 100000)  # Convert to percentage for Office
                    
                    # Try to access the picture element and set alpha
                    pic_element = logo_shape.element
                    if pic_element is not None:
                        # This is a more complex approach but might work better
                        pass  # Keep the default opacity for now if complex method needed
                        
            except Exception as e:
                print(f"Could not set logo opacity: {e}")
                # Logo will still be added, just without opacity adjustment
            
            print(f"✅ Added background logo with opacity {opacity}")
            
        except Exception as e:
            print(f"Could not add background logo: {e}")
    
    def _create_title_slide(self, prs, company_name, identity_data, brand_essence):
        """Create professional title slide with black background and enhanced layout"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        
        # Pitch black background instead of gradient
        self._add_slide_background(slide, gradient=False, identity_data=identity_data, bg_color='pitch_black')
        
        # FULL BACKGROUND LOGO with slight opacity reduction
        self._add_logo_as_background(slide, identity_data, opacity=0.85)
        
        # Get dynamic primary color from brand palette
        primary_color = "#FFFFFF"  # Default white
        if identity_data and identity_data.get("palette"):
            palette = identity_data["palette"]
            primary_color = self._get_brand_color(palette, "primary", "#FFFFFF")
        
        # RIGHT SIDE: Dynamic colored line above "Brand Identity System"
        line_left, line_top, line_width, line_height = self.grid.get_position(9, 7, 3, 2)
        line_shape = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, 
            line_left, line_top, 
            line_left + line_width, line_top
        )
        # Set line color to brand primary color
        line_rgb = self._hex_to_rgb(primary_color)
        line_shape.line.color.rgb = RGBColor(*line_rgb)
        line_shape.line.width = Pt(0)
        
        # RIGHT SIDE: "Brand Identity System" text centered below line
        left, top, width, height = self.grid.get_position(9, 7, 3, 2)
        brand_system_textbox = slide.shapes.add_textbox(left, top, width, height)
        brand_system_frame = brand_system_textbox.text_frame
        brand_system_frame.text = "Brand Identity System"
        brand_system_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
        self.styler.apply_subtitle_style(brand_system_frame.paragraphs[0], size=18, color=primary_color)
        brand_system_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        brand_system_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    def _create_introduction_slide(self, prs, company_name, brand_essence, identity_data, 
                                  industry="", values="", audience=""):
        """Create introduction slide with AI-generated company overview"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_background(slide, gradient=False, identity_data=identity_data, bg_color='pitch_black')
        
        # Get brand primary color (ensure it uses the agent's chosen primary color)
        primary_color_hex = "#FFFF00"  # Default to yellow
        if identity_data and identity_data.get("palette"):
            palette = identity_data["palette"]
            primary_color_hex = self._get_brand_color(palette, "primary", "#FFFF00")
        
        primary_color_rgb = RGBColor(*self._hex_to_rgb(primary_color_hex))
        
        # Generate AI-powered introduction content
        print("  🤖 Generating AI-powered introduction content...")
        try:
            intro_content = self.introduction_agent.generate_introduction(
                company_name, industry, values, audience, brand_essence
            )
        except Exception as e:
            print(f"  ⚠️ AI introduction generation failed, using fallback: {e}")
            # Fallback to original content
            intro_content = f"The following brand identity system for {company_name}\nis thoughtfully crafted to present our brand in\nan international, engaging, consistent, recognisable\nand proprietary way. Unique in form, versatile in its\napplication and unified by a fundamental principle."
        
        # Content positioned in upper portion - reduced top space and increased width
        left, top, width, height = self.grid.get_position(0.5, 0.8, 10, 4)
        content_textbox = slide.shapes.add_textbox(left, top, width, height)
        content_frame = content_textbox.text_frame
        content_frame.text = intro_content
        content_frame.word_wrap = True
        content_frame.margin_left = 0
        content_frame.margin_right = 0
        content_frame.margin_top = 0
        content_frame.margin_bottom = 0
        
        # Style the content text - white, left-aligned, same as index slide
        for paragraph in content_frame.paragraphs:
            self.styler.apply_body_style(paragraph, color='white', size=20)
            paragraph.alignment = PP_ALIGN.LEFT
            paragraph.space_after = Pt(8)  # Consistent spacing
        
        # Full-width line separator (same width as index slide)
        line_top = self.grid.get_position(1, 6, 1, 0.1)[1]
        line_shape = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            Inches(0.5), line_top,
            Inches(9.5), line_top
        )
        line_shape.line.color.rgb = primary_color_rgb
        line_shape.line.width = Pt(2)
        
        # "INTRODUCTION" title in primary color below the line
        title_top = line_top + Inches(0.3)
        title_textbox = slide.shapes.add_textbox(
            self.grid.get_position(0.5, 6.5, 1, 0.8)[0], title_top,
            Inches(4), Inches(0.8)
        )
        title_frame = title_textbox.text_frame
        title_frame.text = "INTRODUCTION"
        self.styler.apply_title_style(title_frame.paragraphs[0], size=28, color=primary_color_hex)
        title_frame.paragraphs[0].font.bold = True
        title_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
        
        
        
       


    def _create_brand_purpose_slide(self, prs, brand_essence, identity_data, 
                                   company_name="", industry="", values="", audience=""):
        """Create brand purpose slide with AI-generated mission and values"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_background(slide, gradient=False, identity_data=identity_data, bg_color='pitch_black')
        
        # Get brand primary color (ensure it uses the agent's chosen primary color)
        primary_color_hex = "#FFFF00"  # Default to yellow
        if identity_data and identity_data.get("palette"):
            palette = identity_data["palette"]
            primary_color_hex = self._get_brand_color(palette, "primary", "#FFFF00")
        
        primary_color_rgb = RGBColor(*self._hex_to_rgb(primary_color_hex))
        
        # Generate AI-powered brand purpose content
        print("  🤖 Generating AI-powered brand purpose content...")
        try:
            purpose_data = self.brand_purpose_agent.generate_brand_purpose(
                company_name, industry, values, audience, brand_essence
            )
            purpose_content = purpose_data.get("full_content", "")
        except Exception as e:
            print(f"  ⚠️ AI brand purpose generation failed, using fallback: {e}")
            # Fallback content (without "Our Purpose" title)
            purpose_content = ""
            
            if brand_essence and brand_essence.get("brand_positioning"):
                positioning = brand_essence["brand_positioning"]
                if positioning.get("unique_value_proposition"):
                    purpose_content += f"Vision: {positioning['unique_value_proposition']}\n\n"
                if positioning.get("brand_promise"):
                    purpose_content += f"Mission: {positioning['brand_promise']}\n\n"
            
            # Add core values if available
            if brand_essence and brand_essence.get("company_profile", {}).get("core_values"):
                brand_values = brand_essence["company_profile"]["core_values"]
                purpose_content += f"Core Values:\n"
                for value in brand_values:
                    purpose_content += f"• {value}\n"
            else:
                purpose_content += "Core Values:\nOur core values guide everything we do, from innovation to customer service excellence."
        
        # Main content text - positioned in upper area (same as Introduction)
        # Content positioned in upper portion - reduced top space and increased width
        left, top, width, height = self.grid.get_position(0.5, 0.8, 10, 4)
        content_textbox = slide.shapes.add_textbox(left, top, width, height)
        content_frame = content_textbox.text_frame
        content_frame.text = purpose_content
        content_frame.word_wrap = True
        content_frame.margin_left = 0
        content_frame.margin_right = 0
        content_frame.margin_top = 0
        content_frame.margin_bottom = 0
        
        # Style the content text - white, left-aligned, same as introduction slide
        for paragraph in content_frame.paragraphs:
            self.styler.apply_body_style(paragraph, color='white', size=20)
            paragraph.alignment = PP_ALIGN.LEFT
            paragraph.space_after = Pt(8)  # Consistent spacing
        
        # Full-width line separator (same width as introduction slide)
        line_top = self.grid.get_position(1, 6, 1, 0.1)[1]
        line_shape = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            Inches(0.5), line_top,
            Inches(9.5), line_top
        )
        line_shape.line.color.rgb = primary_color_rgb
        line_shape.line.width = Pt(2)
        
        # "BRAND PURPOSE" title in primary color below the line (same as Introduction)
        title_top = line_top + Inches(0.3)
        title_textbox = slide.shapes.add_textbox(
            self.grid.get_position(0.5, 6.5, 1, 0.8)[0], title_top,
            Inches(4), Inches(0.8)
        )
        title_frame = title_textbox.text_frame
        title_frame.text = "BRAND PURPOSE"
        self.styler.apply_title_style(title_frame.paragraphs[0], size=28, color=primary_color_hex)
        title_frame.paragraphs[0].font.bold = True
        title_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
        


    
    def _create_table_of_contents(self, prs, sections, identity_data):
        """Create auto-generated table of contents with INDEX design pattern"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        
        # Pitch black background
        self._add_slide_background(slide, gradient=False, identity_data=identity_data, bg_color='pitch_black')
        
        # Get brand primary color from AI research
        primary_color_hex = "#FFFFFF"  # Default white
        if identity_data and identity_data.get("palette"):
            palette = identity_data["palette"]
            primary_color_hex = self._get_brand_color(palette, "primary", "#FFFFFF")
        
        primary_rgb = RGBColor(*self._hex_to_rgb(primary_color_hex))
        
        # Filter sections (remove Table of Contents from list)
        filtered_sections = [s for s in sections if s != "Table of Contents"]
        
        # Map our actual slides to index format with page numbers
        section_data = []
        page_num = 1
        
        for section in filtered_sections:
            section_name = section.replace("1. ", "").replace("2. ", "").replace("3. ", "").replace("4. ", "").replace("5. ", "").replace("6. ", "").replace("7. ", "").replace("8. ", "").replace("9. ", "").replace("10. ", "").replace("11. ", "").replace("12. ", "").replace("13. ", "").replace("14. ", "")
            
            if "Logo" in section_name:
                section_data.append({
                    "name": "Logo Variations",
                    "page": f"{page_num:02d}",
                    "subsections": ["Logo Mark", "Clear Space", "Usage Guidelines"]
                })
            elif "Color" in section_name:
                section_data.append({
                    "name": "Brand Colors",
                    "page": f"{page_num:02d}",
                    "subsections": ["Primary Colors", "Secondary Colors", "Color Usage"]
                })
            elif "Typography" in section_name:
                section_data.append({
                    "name": "Typography",
                    "page": f"{page_num:02d}",
                    "subsections": ["Brand Font", "Font Usage", "Text Hierarchy"]
                })
            elif "Visual" in section_name:
                section_data.append({
                    "name": "Visual Guidelines",
                    "page": f"{page_num:02d}",
                    "subsections": ["Visual Style", "Photography", "Imagery"]
                })
            else:
                section_data.append({
                    "name": section_name,
                    "page": f"{page_num:02d}",
                    "subsections": []
                })
            page_num += 1
        
        # Three-column layout
        col1_left = Inches(0.5)
        col2_left = Inches(3.8)
        col3_left = Inches(7.1)
        
        # Split sections into three columns
        items_per_col = len(section_data) // 3 + (1 if len(section_data) % 3 > 0 else 0)
        col1_sections = section_data[:items_per_col]
        col2_sections = section_data[items_per_col:items_per_col*2]
        col3_sections = section_data[items_per_col*2:]
        
        # "INDEX" title at top (brand colored text, bold)
        index_textbox = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.5),
            Inches(3), Inches(0.8)
        )
        index_frame = index_textbox.text_frame
        index_frame.text = "INDEX"
        self.styler.apply_title_style(index_frame.paragraphs[0], size=28, color=primary_color_hex)
        index_frame.paragraphs[0].font.bold = True
        
        # Top brand colored line (full width)
        top_line_top = Inches(1.2)
        top_line = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            Inches(0.5), top_line_top,
            Inches(9.5), top_line_top
        )
        top_line.line.color.rgb = primary_rgb
        top_line.line.width = Pt(2)
        
        # Create content for each column
        def create_column_content(slide, sections, col_left, start_top=1.7):
            current_top = start_top
            
            for section in sections:
                # Main section with brand colored line and page number
                section_top = Inches(current_top)
                
                # Section name (white text, smaller) - reduced width for closer gap
                section_textbox = slide.shapes.add_textbox(col_left, section_top, 
                                                         Inches(2.0), Inches(0.3))
                section_frame = section_textbox.text_frame
                section_frame.text = section["name"]
                section_frame.margin_left = 0
                section_frame.margin_right = 0
                section_frame.margin_top = 0
                section_frame.margin_bottom = 0
                self.styler.apply_body_style(section_frame.paragraphs[0], size=12, color='white')
                section_frame.paragraphs[0].font.bold = True
                
                # Brand colored accent line (moved closer)
                line_left = col_left + Inches(2.05)
                line_top = section_top + Inches(0.12)
                line_shape = slide.shapes.add_connector(
                    MSO_CONNECTOR.STRAIGHT,
                    line_left, line_top,
                    line_left + Inches(0.4), line_top
                )
                line_shape.line.color.rgb = primary_rgb
                line_shape.line.width = Pt(1.5)
                
                # Page number (brand colored text, smaller) - moved closer
                page_left = col_left + Inches(2.5)
                page_textbox = slide.shapes.add_textbox(page_left, section_top, 
                                                       Inches(0.3), Inches(0.3))
                page_frame = page_textbox.text_frame
                page_frame.text = section["page"]
                page_frame.margin_left = 0
                page_frame.margin_top = 0
                page_frame.margin_bottom = 0
                self.styler.apply_body_style(page_frame.paragraphs[0], size=12, color=primary_color_hex)
                page_frame.paragraphs[0].font.bold = True
                
                current_top += 0.4
                
                # Add subsections (gray text, indented, smaller)
                for subsection in section["subsections"]:
                    sub_top = Inches(current_top)
                    sub_left = col_left + Inches(0.2)  # Indent subsections
                    
                    sub_textbox = slide.shapes.add_textbox(sub_left, sub_top, 
                                                          Inches(2.0), Inches(0.25))
                    sub_frame = sub_textbox.text_frame
                    sub_frame.text = subsection
                    sub_frame.margin_left = 0
                    sub_frame.margin_top = 0
                    sub_frame.margin_bottom = 0
                    self.styler.apply_body_style(sub_frame.paragraphs[0], size=9, color='#CCCCCC')
                    
                    current_top += 0.25
                
                current_top += 0.15  # Smaller space between main sections
        
        # Create all three columns
        if col1_sections:
            create_column_content(slide, col1_sections, col1_left)
        if col2_sections:
            create_column_content(slide, col2_sections, col2_left)
        if col3_sections:
            create_column_content(slide, col3_sections, col3_left)
        
        
        

    
    def _create_company_profile_slide(self, prs, brand_essence, identity_data):
        """Create company profile with key-value layout and value chips"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_background(slide)
        
        # Title
        left, top, width, height = self.grid.get_position(1, 0, 10, 1)
        title_textbox = slide.shapes.add_textbox(left, top, width, height)
        title_frame = title_textbox.text_frame
        title_frame.text = "Company Profile"
        self.styler.apply_title_style(title_frame.paragraphs[0])
        
        profile = brand_essence.get("company_profile", {})
        
        # Left side - Key facts
        left, top, width, height = self.grid.get_position(1, 2, 5, 4)
        facts_textbox = slide.shapes.add_textbox(left, top, width, height)
        facts_frame = facts_textbox.text_frame
        
        facts_content = []
        if profile.get('name'):
            facts_content.append(f"Company: {profile['name']}")
        if profile.get('industry'):
            facts_content.append(f"Industry: {profile['industry']}")
        if profile.get('target_audience'):
            facts_content.append(f"Target Audience: {profile['target_audience']}")
        
        facts_frame.text = "\n\n".join(facts_content)
        facts_frame.word_wrap = True
        for paragraph in facts_frame.paragraphs:
            self.styler.apply_body_style(paragraph, size=16)
        
        # Right side - Core values as chips
        if profile.get('core_values'):
            values = profile['core_values']
            palette = identity_data.get("palette", {}) if identity_data else {}
            accent_color = self._get_brand_color(palette, "accent", "#4A90E2")
            secondary_color = self._get_brand_color(palette, "secondary", "#6C757D")
            
            chip_colors = [accent_color, secondary_color]
            
            for i, value in enumerate(values[:6]):  # Limit to 6 values
                row = 2 + (i // 2)
                col = 7 + (i % 2) * 2
                
                left, top, width, height = self.grid.get_position(col, row, 2, 1)
                
                # Create chip background
                chip_bg = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE, 
                    left, top + Inches(0.1), 
                    width - Inches(0.1), height - Inches(0.2)
                )
                chip_bg.fill.solid()
                color = chip_colors[i % len(chip_colors)]
                chip_bg.fill.fore_color.rgb = RGBColor(*self._hex_to_rgb(color))
                chip_bg.line.fill.background()
                
                # Add text on chip
                chip_textbox = slide.shapes.add_textbox(left, top, width, height)
                chip_frame = chip_textbox.text_frame
                chip_frame.text = value
                chip_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
                chip_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
                self.styler.apply_body_style(chip_frame.paragraphs[0], "#FFFFFF", size=14)
        
       
    
    def _create_market_analysis_slide(self, prs, brand_essence, identity_data):
        """Create market analysis with organized blocks"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_background(slide)
        
        # Title
        left, top, width, height = self.grid.get_position(1, 0, 10, 1)
        title_textbox = slide.shapes.add_textbox(left, top, width, height)
        title_frame = title_textbox.text_frame
        title_frame.text = "Market Analysis & Insights"
        self.styler.apply_title_style(title_frame.paragraphs[0])
        
        analysis = brand_essence.get("market_analysis", {})
        
        # Industry Trends block
        if analysis.get("industry_trends"):
            left, top, width, height = self.grid.get_position(1, 2, 4, 2)
            trends_textbox = slide.shapes.add_textbox(left, top, width, height)
            trends_frame = trends_textbox.text_frame
            trends_content = ["Industry Trends:"] + [f"• {trend}" for trend in analysis["industry_trends"][:5]]
            trends_frame.text = "\n".join(trends_content)
            trends_frame.word_wrap = True
            for i, paragraph in enumerate(trends_frame.paragraphs):
                if i == 0:
                    self.styler.apply_subtitle_style(paragraph, size=18)
                else:
                    self.styler.apply_body_style(paragraph, size=14)
        
        # Competitors block
        if analysis.get("competitor_insights", {}).get("notable_competitors"):
            left, top, width, height = self.grid.get_position(5, 2, 4, 2)
            competitors_textbox = slide.shapes.add_textbox(left, top, width, height)
            competitors_frame = competitors_textbox.text_frame
            competitors = analysis["competitor_insights"]["notable_competitors"][:6]
            competitors_content = ["Key Competitors:"] + [f"• {comp}" for comp in competitors]
            competitors_frame.text = "\n".join(competitors_content)
            competitors_frame.word_wrap = True
            for i, paragraph in enumerate(competitors_frame.paragraphs):
                if i == 0:
                    self.styler.apply_subtitle_style(paragraph, size=18)
                else:
                    self.styler.apply_body_style(paragraph, size=14)
        
        # Design Styles block
        if analysis.get("design_trends", {}).get("design_styles"):
            left, top, width, height = self.grid.get_position(9, 2, 3, 2)
            styles_textbox = slide.shapes.add_textbox(left, top, width, height)
            styles_frame = styles_textbox.text_frame
            styles = analysis["design_trends"]["design_styles"][:4]
            styles_content = ["Design Styles:"] + [f"• {style}" for style in styles]
            styles_frame.text = "\n".join(styles_content)
            styles_frame.word_wrap = True
            for i, paragraph in enumerate(styles_frame.paragraphs):
                if i == 0:
                    self.styler.apply_subtitle_style(paragraph, size=18)
                else:
                    self.styler.apply_body_style(paragraph, size=14)
        
        self._add_footer(slide, self.slide_counter)
    
    def _create_brand_positioning_slide(self, prs, brand_essence, identity_data):
        """Create brand positioning with grid layout"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_background(slide)
        
        # Title
        left, top, width, height = self.grid.get_position(1, 0, 10, 1)
        title_textbox = slide.shapes.add_textbox(left, top, width, height)
        title_frame = title_textbox.text_frame
        title_frame.text = "Brand Positioning"
        self.styler.apply_title_style(title_frame.paragraphs[0])
        
        positioning = brand_essence.get("brand_positioning", {})
        
        # UVP box (top left)
        if positioning.get('unique_value_proposition'):
            left, top, width, height = self.grid.get_position(1, 2, 6, 2)
            uvp_textbox = slide.shapes.add_textbox(left, top, width, height)
            uvp_frame = uvp_textbox.text_frame
            uvp_frame.text = f"Unique Value Proposition:\n{positioning['unique_value_proposition']}"
            uvp_frame.word_wrap = True
            self.styler.apply_subtitle_style(uvp_frame.paragraphs[0], size=16)
            for paragraph in uvp_frame.paragraphs[1:]:
                self.styler.apply_body_style(paragraph, size=14)
        
        # Brand Promise box (top right)
        if positioning.get('brand_promise'):
            left, top, width, height = self.grid.get_position(7, 2, 5, 2)
            promise_textbox = slide.shapes.add_textbox(left, top, width, height)
            promise_frame = promise_textbox.text_frame
            promise_frame.text = f"Brand Promise:\n{positioning['brand_promise']}"
            promise_frame.word_wrap = True
            self.styler.apply_subtitle_style(promise_frame.paragraphs[0], size=16)
            for paragraph in promise_frame.paragraphs[1:]:
                self.styler.apply_body_style(paragraph, size=14)
        
        # Brand Personality chips (middle)
        if positioning.get('brand_personality'):
            personalities = positioning['brand_personality']
            palette = identity_data.get("palette", {}) if identity_data else {}
            accent_color = self._get_brand_color(palette, "accent", "#4A90E2")
            
            for i, personality in enumerate(personalities[:5]):
                col = 1 + i * 2
                left, top, width, height = self.grid.get_position(col, 4, 2, 1)
                
                # Create chip
                chip_bg = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    left, top + Inches(0.1),
                    width - Inches(0.1), height - Inches(0.2)
                )
                chip_bg.fill.solid()
                chip_bg.fill.fore_color.rgb = RGBColor(*self._hex_to_rgb(accent_color))
                chip_bg.fill.transparency = 0.2
                chip_bg.line.color.rgb = RGBColor(*self._hex_to_rgb(accent_color))
                chip_bg.line.width = Pt(1)
                
                # Add text
                chip_textbox = slide.shapes.add_textbox(left, top, width, height)
                chip_frame = chip_textbox.text_frame
                chip_frame.text = personality
                chip_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
                chip_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
                self.styler.apply_body_style(chip_frame.paragraphs[0], size=12)
        
        # Competitive Advantage (bottom)
        if positioning.get('competitive_advantage'):
            left, top, width, height = self.grid.get_position(1, 5, 11, 2)
            advantage_textbox = slide.shapes.add_textbox(left, top, width, height)
            advantage_frame = advantage_textbox.text_frame
            advantage_frame.text = f"Competitive Advantage:\n{positioning['competitive_advantage']}"
            advantage_frame.word_wrap = True
            self.styler.apply_subtitle_style(advantage_frame.paragraphs[0], size=16)
            for paragraph in advantage_frame.paragraphs[1:]:
                self.styler.apply_body_style(paragraph, size=14)
        
        self._add_footer(slide, self.slide_counter)
    
    def _create_logo_variations_slide(self, prs, logos, identity_data):
        """Create logo variations with grid layout and clearspace guidelines"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_background(slide)
        
        # Title
        left, top, width, height = self.grid.get_position(1, 0, 10, 1)
        title_textbox = slide.shapes.add_textbox(left, top, width, height)
        title_frame = title_textbox.text_frame
        title_frame.text = f"Logo Variations ({len(logos)} designs)"
        self.styler.apply_title_style(title_frame.paragraphs[0])
        
        # Arrange logos in grid
        logo_col = 1
        logo_row = 2
        logos_per_row = 3
        logo_size = 2
        
        for i, logo_path in enumerate(logos):
            if os.path.exists(logo_path):
                try:
                    left, top, width, height = self.grid.get_position(
                        logo_col, logo_row, logo_size, logo_size)
                    
                    # Add background for logo
                    bg_shape = slide.shapes.add_shape(
                        MSO_SHAPE.RECTANGLE,
                        left - Inches(0.1), top - Inches(0.1),
                        width + Inches(0.2), height + Inches(0.2)
                    )
                    bg_shape.fill.solid()
                    bg_shape.fill.fore_color.rgb = RGBColor(255, 255, 255)
                    bg_shape.fill.transparency = 0.1
                    bg_shape.line.fill.background()
                    
                    # Add logo
                    slide.shapes.add_picture(logo_path, left, top, width=width, height=height)
                    
                    # Add label
                    label_left, label_top, label_width, label_height = self.grid.get_position(
                        logo_col, logo_row + logo_size, logo_size, 1)
                    label_textbox = slide.shapes.add_textbox(
                        label_left, label_top, label_width, label_height)
                    label_frame = label_textbox.text_frame
                    label_frame.text = f"Version {i+1}"
                    label_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
                    self.styler.apply_caption_style(label_frame.paragraphs[0])
                    
                    # Move to next position
                    logo_col += logo_size + 1
                    if logo_col > 12 - logo_size:
                        logo_col = 1
                        logo_row += logo_size + 2
                    
                except Exception as e:
                    print(f"Error adding logo {i+1}: {e}")
        
        # Add minimum size and clearspace info if we have logos
        if logos and any(os.path.exists(logo) for logo in logos):
            info_left, info_top, info_width, info_height = self.grid.get_position(1, 6, 11, 1)
            info_textbox = slide.shapes.add_textbox(info_left, info_top, info_width, info_height)
            info_frame = info_textbox.text_frame
            info_frame.text = "Minimum size: 0.5 inches • Clearspace: 0.25 inches on all sides"
            info_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            self.styler.apply_caption_style(info_frame.paragraphs[0])
        
        self._add_footer(slide, self.slide_counter)
    
    def _create_color_palette_slide(self, prs, palette, identity_data):
        """Create comprehensive color palette with accessibility info"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_background(slide)
        
        # Title
        left, top, width, height = self.grid.get_position(1, 0, 10, 1)
        title_textbox = slide.shapes.add_textbox(left, top, width, height)
        title_frame = title_textbox.text_frame
        title_frame.text = "Color Palette"
        self.styler.apply_title_style(title_frame.paragraphs[0])
        
        # Color swatches with detailed info
        col = 1
        row = 2
        colors_per_row = 3
        
        for i, (color_name, hex_code) in enumerate(palette.items()):
            if isinstance(hex_code, list):
                hex_code = hex_code[0] if hex_code else "#CCCCCC"
            hex_code = (hex_code or "#CCCCCC").lstrip("#")
            
            if len(hex_code) == 3:
                hex_code = ''.join([c*2 for c in hex_code])
            if len(hex_code) != 6:
                hex_code = "CCCCCC"
            
            try:
                rgb = tuple(int(hex_code[j:j+2], 16) for j in (0, 2, 4))
            except Exception:
                rgb = (204, 204, 204)
            
            left, top, width, height = self.grid.get_position(col, row, 3, 2)
            
            # Color swatch
            swatch = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, left, top, width, height
            )
            swatch.fill.solid()
            swatch.fill.fore_color.rgb = RGBColor(*rgb)
            swatch.line.color.rgb = RGBColor(255, 255, 255)
            swatch.line.width = Pt(1)
            
            # Color info below swatch
            info_left, info_top, info_width, info_height = self.grid.get_position(col, row + 2, 3, 2)
            info_textbox = slide.shapes.add_textbox(info_left, info_top, info_width, info_height)
            info_frame = info_textbox.text_frame
            
            # Calculate CMYK (approximation)
            r, g, b = [x/255.0 for x in rgb]
            k = 1 - max(r, g, b)
            c = (1-r-k) / (1-k) if k < 1 else 0
            m = (1-g-k) / (1-k) if k < 1 else 0
            y = (1-b-k) / (1-k) if k < 1 else 0
            
            # Determine text readability
            brightness = sum(rgb) / 3
            text_suggestion = "Use Light Text" if brightness < 128 else "Use Dark Text"
            
            info_content = f"{color_name.title()}\n#{hex_code.upper()}\nRGB({rgb[0]}, {rgb[1]}, {rgb[2]})\nCMYK({int(c*100)}, {int(m*100)}, {int(y*100)}, {int(k*100)})\n{text_suggestion}"
            info_frame.text = info_content
            info_frame.word_wrap = True
            
            for paragraph in info_frame.paragraphs:
                self.styler.apply_caption_style(paragraph, size=10)
            
            # Move to next position
            col += 4
            if col > 12 - 3:
                col = 1
                row += 5
        
        self._add_footer(slide, self.slide_counter)
    
    def _create_typography_slide(self, prs, typography, identity_data):
        """Create typography showcase with different weights and sizes"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_background(slide)
        
        # Title
        left, top, width, height = self.grid.get_position(1, 0, 10, 1)
        title_textbox = slide.shapes.add_textbox(left, top, width, height)
        title_frame = title_textbox.text_frame
        title_frame.text = "Typography"
        self.styler.apply_title_style(title_frame.paragraphs[0])
        
        # Font information
        primary_font = self.styler.primary_font
        secondary_font = self.styler.secondary_font
        
        # Primary font showcase
        left, top, width, height = self.grid.get_position(1, 2, 5, 1)
        primary_title_box = slide.shapes.add_textbox(left, top, width, height)
        primary_title_frame = primary_title_box.text_frame
        primary_title_frame.text = f"Primary Font: {primary_font}"
        self.styler.apply_subtitle_style(primary_title_frame.paragraphs[0], size=20)
        
        # Primary font samples
        samples = [
            ("H1 Heading", 32, True),
            ("H2 Heading", 24, True),
            ("H3 Heading", 20, False),
        ]
        
        for i, (sample_text, size, bold) in enumerate(samples):
            left, top, width, height = self.grid.get_position(1, 3 + i, 5, 1)
            sample_box = slide.shapes.add_textbox(left, top, width, height)
            sample_frame = sample_box.text_frame
            sample_frame.text = sample_text
            sample_frame.paragraphs[0].font.name = primary_font
            sample_frame.paragraphs[0].font.size = Pt(size)
            sample_frame.paragraphs[0].font.bold = bold
            sample_frame.paragraphs[0].font.color.rgb = RGBColor(*self._hex_to_rgb(self.styler.text_color))
        
        # Secondary font showcase
        left, top, width, height = self.grid.get_position(7, 2, 5, 1)
        secondary_title_box = slide.shapes.add_textbox(left, top, width, height)
        secondary_title_frame = secondary_title_box.text_frame
        secondary_title_frame.text = f"Secondary Font: {secondary_font}"
        self.styler.apply_subtitle_style(secondary_title_frame.paragraphs[0], size=20)
        
        # Secondary font samples
        body_samples = [
            ("Body Text", 16, False),
            ("Body Bold", 16, True),
            ("Caption Text", 12, False),
        ]
        
        for i, (sample_text, size, bold) in enumerate(body_samples):
            left, top, width, height = self.grid.get_position(7, 3 + i, 5, 1)
            sample_box = slide.shapes.add_textbox(left, top, width, height)
            sample_frame = sample_box.text_frame
            sample_frame.text = sample_text
            sample_frame.paragraphs[0].font.name = secondary_font
            sample_frame.paragraphs[0].font.size = Pt(size)
            sample_frame.paragraphs[0].font.bold = bold
            sample_frame.paragraphs[0].font.color.rgb = RGBColor(*self._hex_to_rgb(self.styler.text_color))
        
        self._add_footer(slide, self.slide_counter)
    
    def _create_visual_guidelines_slide(self, prs, visual_style, photography_style, identity_data):
        """Create visual and photography guidelines slide"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_background(slide)
        
        # Title
        left, top, width, height = self.grid.get_position(1, 0, 10, 1)
        title_textbox = slide.shapes.add_textbox(left, top, width, height)
        title_frame = title_textbox.text_frame
        title_frame.text = "Visual & Photography Guidelines"
        self.styler.apply_title_style(title_frame.paragraphs[0])
        
        # Left side - Visual style bullets
        left, top, width, height = self.grid.get_position(1, 2, 5, 4)
        visual_textbox = slide.shapes.add_textbox(left, top, width, height)
        visual_frame = visual_textbox.text_frame
        
        visual_content = ["Visual Style Guidelines:"]
        if visual_style:
            visual_points = visual_style.split(",")
            for point in visual_points[:5]:
                visual_content.append(f"• {point.strip()}")
        
        visual_frame.text = "\n".join(visual_content)
        visual_frame.word_wrap = True
        self.styler.apply_subtitle_style(visual_frame.paragraphs[0], size=18)
        for paragraph in visual_frame.paragraphs[1:]:
            self.styler.apply_body_style(paragraph, size=14)
        
        # Right side - Photography style
        right_left, right_top, right_width, right_height = self.grid.get_position(7, 2, 5, 4)
        photo_textbox = slide.shapes.add_textbox(right_left, right_top, right_width, right_height)
        photo_frame = photo_textbox.text_frame
        
        photo_content = ["Photography Guidelines:"]
        if photography_style:
            photo_points = photography_style.split(",")
            for point in photo_points[:5]:
                photo_content.append(f"• {point.strip()}")
        
        photo_frame.text = "\n".join(photo_content)
        photo_frame.word_wrap = True
        self.styler.apply_subtitle_style(photo_frame.paragraphs[0], size=18)
        for paragraph in photo_frame.paragraphs[1:]:
            self.styler.apply_body_style(paragraph, size=14)
        
        # Placeholder rectangles for example images
        for i in range(3):
            col = 7 + i * 2
            placeholder_left, placeholder_top, placeholder_width, placeholder_height = self.grid.get_position(col, 6, 1, 1)
            placeholder = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                placeholder_left, placeholder_top,
                placeholder_width, placeholder_height
            )
            placeholder.fill.solid()
            placeholder.fill.fore_color.rgb = RGBColor(64, 64, 64)
            placeholder.line.color.rgb = RGBColor(128, 128, 128)
            placeholder.line.width = Pt(1)
            
            # Add "Example Image" text
            img_text = slide.shapes.add_textbox(
                placeholder_left, placeholder_top + placeholder_height/3,
                placeholder_width, placeholder_height/3
            )
            img_frame = img_text.text_frame
            img_frame.text = "Example"
            img_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            self.styler.apply_caption_style(img_frame.paragraphs[0], size=8)
        
        self._add_footer(slide, self.slide_counter)
    
    def _create_text_slide(self, prs, title, content, max_words=80, identity_data=None):
        """Create text-based slide with pagination if needed"""
        chunks = self._paginate_text(content, max_words)
        
        for idx, chunk in enumerate(chunks):
            self.slide_counter += 1
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            self._add_slide_background(slide)
            
            # Title with pagination indicator if multiple slides
            left, top, width, height = self.grid.get_position(1, 0, 10, 1)
            title_textbox = slide.shapes.add_textbox(left, top, width, height)
            title_frame = title_textbox.text_frame
            slide_title = f"{title} ({idx+1}/{len(chunks)})" if len(chunks) > 1 else title
            title_frame.text = slide_title
            self.styler.apply_title_style(title_frame.paragraphs[0])
            
            # Content
            left, top, width, height = self.grid.get_position(1, 2, 10, 4)
            content_textbox = slide.shapes.add_textbox(left, top, width, height)
            content_frame = content_textbox.text_frame
            content_frame.text = chunk
            content_frame.word_wrap = True
            
            for paragraph in content_frame.paragraphs:
                self.styler.apply_body_style(paragraph, size=16)
            
            self._add_footer(slide, self.slide_counter)
    
    def _paginate_text(self, text, words_per_slide=80):
        """Split text into chunks for pagination"""
        if not text or not text.strip():
            return [""]
        
        words = text.split()
        if len(words) <= words_per_slide:
            return [text]
        
        chunks = []
        current_words = []
        
        for word in words:
            current_words.append(word)
            
            if len(current_words) >= words_per_slide:
                if word.endswith('.') or word.endswith('!') or word.endswith('?'):
                    chunks.append(' '.join(current_words))
                    current_words = []
                elif len(current_words) >= words_per_slide + 10:
                    chunks.append(' '.join(current_words))
                    current_words = []
        
        if current_words:
            chunks.append(' '.join(current_words))
        
        return chunks
    
    def _create_brand_purpose_slides(self, prs, brand_essence, identity_data, 
                                    company_name="", industry="", values="", audience=""):
        """Create three separate brand purpose slides: Vision, Mission, Core Values"""
        
        # Generate AI-powered brand purpose content once
        print("  🤖 Generating AI-powered brand purpose content...")
        try:
            purpose_data = self.brand_purpose_agent.generate_brand_purpose(
                company_name, industry, values, audience, brand_essence
            )
            
            # First try to get structured data
            vision_content = purpose_data.get("vision", "")
            mission_content = purpose_data.get("mission", "")
            values_content = purpose_data.get("values_content", "")
            
            # If structured data is missing, parse from full_content
            if not vision_content or not mission_content or not values_content:
                full_content = purpose_data.get("full_content", "")
                if full_content:
                    parsed_vision, parsed_mission, parsed_values = self._parse_brand_purpose_content(full_content)
                    vision_content = parsed_vision or vision_content
                    mission_content = parsed_mission or mission_content  
                    values_content = parsed_values or values_content
            
        except Exception as e:
            print(f"  ⚠️ AI brand purpose generation failed, using fallback: {e}")
            # Fallback content
            vision_content = "To be the preferred partner for businesses seeking excellence and innovation in their field."
            mission_content = "We deliver exceptional solutions that drive growth and create lasting value for our clients and communities."
            values_content = "Our principles guide everything we do, from innovation to customer service excellence."
        
        # Create Vision slide
        self._create_single_purpose_slide(prs, identity_data, "BRAND PURPOSE (VISION)", vision_content)
        
        # Create Mission slide  
        self._create_single_purpose_slide(prs, identity_data, "BRAND PURPOSE (MISSION)", mission_content)
        
        # Create Core Values slide
        self._create_single_purpose_slide(prs, identity_data, "BRAND PURPOSE (VALUES)", values_content)
    
    def _parse_brand_purpose_content(self, full_content):
        """Parse full brand purpose content into Vision, Mission, Core Values"""
        if not full_content:
            return "", "", ""
            
        vision = ""
        mission = ""
        values = ""
        
        lines = full_content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Vision:'):
                if current_section and current_content:
                    # Save previous section
                    content = ' '.join(current_content).strip()
                    if current_section == "vision":
                        vision = content
                    elif current_section == "mission":
                        mission = content
                    elif current_section == "values":
                        values = content
                
                current_section = "vision"
                current_content = [line.replace('Vision:', '').strip()]
                
            elif line.startswith('Mission:'):
                if current_section and current_content:
                    # Save previous section
                    content = ' '.join(current_content).strip()
                    if current_section == "vision":
                        vision = content
                    elif current_section == "mission":
                        mission = content
                    elif current_section == "values":
                        values = content
                
                current_section = "mission"
                current_content = [line.replace('Mission:', '').strip()]
                
            elif line.startswith('Core Values:'):
                if current_section and current_content:
                    # Save previous section
                    content = ' '.join(current_content).strip()
                    if current_section == "vision":
                        vision = content
                    elif current_section == "mission":
                        mission = content
                    elif current_section == "values":
                        values = content
                
                current_section = "values"
                current_content = [line.replace('Core Values:', '').strip()]
                
            elif line and current_section:
                current_content.append(line)
        
        # Save the last section
        if current_section and current_content:
            content = ' '.join(current_content).strip()
            if current_section == "vision":
                vision = content
            elif current_section == "mission":
                mission = content
            elif current_section == "values":
                values = content
        
        return vision, mission, values
    
    def _create_single_purpose_slide(self, prs, identity_data, title, content):
        """Create a single brand purpose slide with same design as Introduction slide"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_background(slide, gradient=False, identity_data=identity_data, bg_color='pitch_black')
        
        # Get brand primary color (ensure it uses the agent's chosen primary color)
        primary_color_hex = "#FFFF00"  # Default to yellow
        if identity_data and identity_data.get("palette"):
            palette = identity_data["palette"]
            primary_color_hex = self._get_brand_color(palette, "primary", "#FFFF00")
        
        primary_color_rgb = RGBColor(*self._hex_to_rgb(primary_color_hex))
        
        # Main content text - positioned in upper area (same as Introduction)
        # Content positioned in upper portion - reduced top space and increased width
        left, top, width, height = self.grid.get_position(0.5, 0.8, 10, 4)
        content_textbox = slide.shapes.add_textbox(left, top, width, height)
        content_frame = content_textbox.text_frame
        content_frame.text = content
        content_frame.word_wrap = True
        content_frame.margin_left = 0
        content_frame.margin_right = 0
        content_frame.margin_top = 0
        content_frame.margin_bottom = 0
        
        # Style the content text - white, left-aligned, same as introduction slide
        for paragraph in content_frame.paragraphs:
            self.styler.apply_body_style(paragraph, color='white', size=20)
            paragraph.alignment = PP_ALIGN.LEFT
            paragraph.space_after = Pt(8)  # Consistent spacing
        
        # Full-width line separator (same width as introduction slide)
        line_top = self.grid.get_position(1, 6, 1, 0.1)[1]
        line_shape = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            Inches(0.5), line_top,
            Inches(9.5), line_top
        )
        line_shape.line.color.rgb = primary_color_rgb
        line_shape.line.width = Pt(2)
        
        # Title in primary color below the line (same as Introduction)
        title_top = line_top + Inches(0.3)
        title_textbox = slide.shapes.add_textbox(
            self.grid.get_position(0.5, 6.5, 1, 0.8)[0], title_top,
            Inches(6), Inches(0.8)
        )
        title_frame = title_textbox.text_frame
        title_frame.text = title
        self.styler.apply_title_style(title_frame.paragraphs[0], size=28, color=primary_color_hex)
        title_frame.paragraphs[0].font.bold = True
        title_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
    
    def _create_brand_story_slide(self, prs, identity_data, title, content):
        """Create brand story slide with same design as Introduction slide"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_slide_background(slide, gradient=False, identity_data=identity_data, bg_color='pitch_black')
        
        # Get brand primary color (ensure it uses the agent's chosen primary color)
        primary_color_hex = "#FFFF00"  # Default to yellow
        if identity_data and identity_data.get("palette"):
            palette = identity_data["palette"]
            primary_color_hex = self._get_brand_color(palette, "primary", "#FFFF00")
        
        primary_color_rgb = RGBColor(*self._hex_to_rgb(primary_color_hex))
        
        # Main content text - positioned in upper area (same as Introduction)
        # Content positioned in upper portion - reduced top space and increased width
        left, top, width, height = self.grid.get_position(0.5, 0.8, 10, 4)
        content_textbox = slide.shapes.add_textbox(left, top, width, height)
        content_frame = content_textbox.text_frame
        content_frame.text = content
        content_frame.word_wrap = True
        content_frame.margin_left = 0
        content_frame.margin_right = 0
        content_frame.margin_top = 0
        content_frame.margin_bottom = 0
        
        # Style the content text - white, left-aligned, same as introduction slide
        for paragraph in content_frame.paragraphs:
            self.styler.apply_body_style(paragraph, color='white', size=20)
            paragraph.alignment = PP_ALIGN.LEFT
            paragraph.space_after = Pt(8)  # Consistent spacing
        
        # Full-width line separator (same width as introduction slide)
        line_top = self.grid.get_position(1, 6, 1, 0.1)[1]
        line_shape = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            Inches(0.5), line_top,
            Inches(9.5), line_top
        )
        line_shape.line.color.rgb = primary_color_rgb
        line_shape.line.width = Pt(2)
        
        # Title in primary color below the line (same as Introduction)
        title_top = line_top + Inches(0.3)
        title_textbox = slide.shapes.add_textbox(
            self.grid.get_position(0.5, 6.5, 1, 0.8)[0], title_top,
            Inches(6), Inches(0.8)
        )
        title_frame = title_textbox.text_frame
        title_frame.text = title
        self.styler.apply_title_style(title_frame.paragraphs[0], size=28, color=primary_color_hex)
        title_frame.paragraphs[0].font.bold = True
        title_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
    
    def _create_brand_story_slides(self, prs, identity_data, story_content):
        """Create Brand Story slides - split into multiple slides if content is too long"""
        
        # Split content into manageable chunks for slides
        story_parts = self._split_story_content(story_content)
        
        print(f"  📖 Brand Story split into {len(story_parts)} parts")
        for i, part in enumerate(story_parts):
            word_count = len(part.split())
            print(f"    Part {i+1}: {word_count} words")
        
        if len(story_parts) == 1:
            # Single slide
            self._create_brand_story_slide(prs, identity_data, "BRAND STORY", story_parts[0])
        else:
            # Multiple slides with pagination
            for i, part in enumerate(story_parts):
                slide_title = f"BRAND STORY ({i+1}/{len(story_parts)})"
                self._create_brand_story_slide(prs, identity_data, slide_title, part)
    
    def _split_story_content(self, content):
        """Split story content into appropriate chunks for slides"""
        if not content:
            return [""]
        
        # Target words per slide (roughly 150 words per slide for better readability on slides)
        words_per_slide = 150
        words = content.split()
        
        if len(words) <= words_per_slide:
            return [content]
        
        # Split into paragraphs first
        paragraphs = content.split('\n\n')
        
        parts = []
        current_part = ""
        current_word_count = 0
        
        for paragraph in paragraphs:
            paragraph_words = paragraph.split()
            paragraph_word_count = len(paragraph_words)
            
            # If adding this paragraph would exceed the limit, start a new part
            if current_word_count + paragraph_word_count > words_per_slide and current_part:
                parts.append(current_part.strip())
                current_part = paragraph + "\n\n"
                current_word_count = paragraph_word_count
            else:
                current_part += paragraph + "\n\n"
                current_word_count += paragraph_word_count
        
        # Add the last part if there's content
        if current_part.strip():
            parts.append(current_part.strip())
        
        # If we still don't have good splits, do a simple word-based split
        if not parts or (len(parts) == 1 and len(words) > words_per_slide * 2):
            parts = []
            for i in range(0, len(words), words_per_slide):
                chunk_words = words[i:i + words_per_slide]
                parts.append(' '.join(chunk_words))
        
        return parts if parts else [content]

    def create_pptx(self, company_name, identity_data, literature_data, brand_essence=None, 
                   industry="", values="", audience=""):
        """Create comprehensive brand book presentation with AI-generated content"""
        prs = Presentation()
        
        # Extract input parameters from brand_essence if not provided
        if brand_essence and brand_essence.get("company_profile"):
            profile = brand_essence["company_profile"]
            if not industry:
                industry = profile.get("industry", "technology")
            if not values and profile.get("core_values"):
                values = ", ".join(profile["core_values"])
            if not audience:
                audience = profile.get("target_audience", "businesses")
        
        # Research fonts
        print(f"🎨 Researching fonts for {company_name}...")
        self.researched_fonts = self.font_research_agent.research_fonts(company_name, industry, brand_essence)
        print(f"✅ Selected fonts: {self.researched_fonts['primary_font']} (primary), {self.researched_fonts['secondary_font']} (secondary)")
        
        # Initialize styling system
        self._initialize_styling(identity_data, company_name)
        
        # Create slides
        sections = ["Table of Contents"]
        
        # 1. Title Slide
        self._create_title_slide(prs, company_name, identity_data, brand_essence)
        
        # Build sections list with Introduction and Brand Purpose sections
        sections.extend([
            "1. Introduction",
            "2. Brand Purpose (Vision)",
            "3. Brand Purpose (Mission)", 
            "4. Brand Purpose (Values)",
            "5. Brand Story",
            "6. Logo Variations",
            "7. Color Palette", 
            "8. Typography",
            "9. Visual & Photography Guidelines"
        ])
        
        # 2. Table of Contents
        self._create_table_of_contents(prs, sections, identity_data)
        
        # 3. Introduction Slide with AI content
        self._create_introduction_slide(prs, company_name, brand_essence, identity_data, 
                                       industry, values, audience)
        
        # 4-6. Brand Purpose Slides (Vision, Mission, Core Values) with AI content
        self._create_brand_purpose_slides(prs, brand_essence, identity_data, 
                                         company_name, industry, values, audience)
        
        # 7. Brand Story Slide with AI content
        print("  🤖 Generating AI-powered brand story content...")
        try:
            story_content = self.brand_story_agent.generate_brand_story(
                company_name, industry, values, audience, brand_essence, literature_data
            )
        except Exception as e:
            print(f"  ⚠️ AI brand story generation failed, using fallback: {e}")
            story_content = literature_data.get("brand_story", "") if literature_data else ""
            if not story_content:
                story_content = f"Our story at {company_name} is one of innovation and dedication to excellence."
        
        if story_content:
            self._create_brand_story_slides(prs, identity_data, story_content)
        
        # 8. Logo Variations
        if identity_data.get("logos"):
            print(f"  🎨 Creating logo variations slide with {len(identity_data['logos'])} logos...")
            self._create_logo_variations_slide(prs, identity_data["logos"], identity_data)
        else:
            print("  ⚠️ No logos found in identity_data - skipping logo slide")
        
        # 9. Color Palette
        if identity_data.get("palette"):
            self._create_color_palette_slide(prs, identity_data["palette"], identity_data)
        
        # 10. Typography
        self._create_typography_slide(prs, identity_data.get("typography", {}), identity_data)
        
        # 11. Visual & Photography Guidelines
        self._create_visual_guidelines_slide(
            prs,
            identity_data.get("visual_style", ""),
            identity_data.get("photography_style", ""),
            identity_data
        )
        
        # Save file
        base_name = company_name.lower().replace(' ', '_')
        company_output_dir = os.path.join("output", base_name)
        os.makedirs(company_output_dir, exist_ok=True)
        file_name = f"{base_name}_enhanced_brand_book.pptx"
        file_path = os.path.join(company_output_dir, file_name)
        prs.save(file_path)
        
        print(f"Enhanced Brand Book PPTX saved at: {file_path}")
        return file_path


# For backward compatibility
PPTXGenerator = EnhancedPPTXGenerator

# Example usage
if __name__ == "__main__":
    identity_data = {
        "logos": [],
        "palette": {"primary": "#2E86AB", "secondary": "#A23B72", "accent": "#F18F01"},
        "typography": {"primary": "Inter", "secondary": "Source Sans Pro"},
        "visual_style": "Modern, clean, professional, minimalist, bold typography",
        "photography_style": "High contrast, authentic moments, natural lighting, diverse subjects"
    }
    
    literature_data = {
        "brand_story": "Our company revolutionizes the way people connect with technology through innovative design and user-centered solutions.",
        "voice_tone": "Professional yet approachable, confident, innovative, and human-centered.",
        "messaging_arch": "We believe technology should enhance human potential, not complicate it.",
        "marketing_copy": {
            "website": "Transform your digital experience with our cutting-edge solutions.",
            "social_media": "Innovation meets simplicity. #TechForHumans"
        },
        "collaterals": {
            "business_card": "Clean, modern design with QR code integration",
            "letterhead": "Professional header with brand elements"
        }
    }
    
    brand_essence = {
        "company_profile": {
            "name": "TechForward Inc",
            "industry": "Technology",
            "target_audience": "Progressive businesses seeking digital transformation",
            "core_values": ["Innovation", "Simplicity", "Human-Centered", "Excellence"]
        },
        "brand_positioning": {
            "unique_value_proposition": "We bridge the gap between complex technology and intuitive user experiences",
            "brand_promise": "Technology that works for you, not against you",
            "brand_personality": ["Innovative", "Reliable", "Approachable", "Progressive"],
            "competitive_advantage": "Our deep understanding of human psychology drives more intuitive technology solutions"
        }
    }
    
    generator = EnhancedPPTXGenerator()
    generator.create_pptx("TechForward Inc", identity_data, literature_data, brand_essence)