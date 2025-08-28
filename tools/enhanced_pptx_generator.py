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
        """Body text using secondary font"""
        paragraph.font.name = self.secondary_font
        paragraph.font.size = Pt(size)
        paragraph.font.bold = False
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
    
    def _create_title_slide(self, prs, company_name, identity_data, brand_essence):
        """Create professional title slide with black background and enhanced layout"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        
        # Pitch black background instead of gradient
        self._add_slide_background(slide, gradient=False, identity_data=identity_data, bg_color='pitch_black')
        
        # LEFT SIDE: Logo centered in left half
        self._add_logo_to_slide(slide, identity_data, col=1, row=2, size=3, opacity=0.8)
        
        # Get dynamic primary color from brand palette
        primary_color = "#FFFFFF"  # Default white
        if identity_data and identity_data.get("palette"):
            palette = identity_data["palette"]
            primary_color = self._get_brand_color(palette, "primary", "#FFFFFF")
        
        # LEFT SIDE: Company name below logo, centered
        left, top, width, height = self.grid.get_position(1, 5, 4, 1)
        company_textbox = slide.shapes.add_textbox(left, top, width, height)
        company_frame = company_textbox.text_frame
        company_frame.text = company_name
        company_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
        self.styler.apply_title_style(company_frame.paragraphs[0], size=36, color=primary_color)
        company_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        
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
        


    
    def _create_table_of_contents(self, prs, sections, identity_data):
        """Create auto-generated table of contents with two-column layout if needed"""
        self.slide_counter += 1
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        # Pitch black background instead of gradient
        self._add_slide_background(slide, gradient=False, identity_data=identity_data, bg_color='pitch_black')
        
        
        # Title
        left, top, width, height = self.grid.get_position(1, 0, 10, 1)
        title_textbox = slide.shapes.add_textbox(left, top, width, height)
        title_frame = title_textbox.text_frame
        title_frame.text = "Table of Contents"
        self.styler.apply_title_style(title_frame.paragraphs[0])
        title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        # Determine if two-column layout is needed
        filtered_sections = [s for s in sections if s != "Table of Contents"]
        use_two_columns = len(filtered_sections) > 8
        
        if use_two_columns:
            # Two-column layout with increased gap
            mid_point = len(filtered_sections) // 2
            col1_sections = filtered_sections[:mid_point]
            col2_sections = filtered_sections[mid_point:]
            
            # Column 1 - Left side with more space
            left, top, width, height = self.grid.get_position(1, 2, 4, 5)
            col1_textbox = slide.shapes.add_textbox(left, top, width, height)
            col1_frame = col1_textbox.text_frame
            col1_content = []
            for i, section in enumerate(col1_sections, 1):
                col1_content.append(f"{i}. {section}")
            col1_frame.text = "\n\n".join(col1_content)
            col1_frame.word_wrap = True
            
            # Column 2 - Right side with bigger gap (moved from col 7 to col 8)
            left, top, width, height = self.grid.get_position(8, 2, 4, 5)
            col2_textbox = slide.shapes.add_textbox(left, top, width, height)
            col2_frame = col2_textbox.text_frame
            col2_content = []
            for i, section in enumerate(col2_sections, mid_point + 1):
                col2_content.append(f"{i}. {section}")
            col2_frame.text = "\n\n".join(col2_content)
            col2_frame.word_wrap = True
            
            # Style both columns
            for frame in [col1_frame, col2_frame]:
                for paragraph in frame.paragraphs:
                    self.styler.apply_body_style(paragraph, size=16)
        else:
            # Single column layout
            left, top, width, height = self.grid.get_position(2, 2, 8, 5)
            content_textbox = slide.shapes.add_textbox(left, top, width, height)
            content_frame = content_textbox.text_frame
            content_lines = []
            for i, section in enumerate(filtered_sections, 1):
                content_lines.append(f"{i}. {section}")
            content_frame.text = "\n\n".join(content_lines)
            content_frame.word_wrap = True
            
            for paragraph in content_frame.paragraphs:
                self.styler.apply_body_style(paragraph, size=16)
        

    
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
        
        self._add_footer(slide, self.slide_counter)
    
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
    
    def create_pptx(self, company_name, identity_data, literature_data, brand_essence=None):
        """Create comprehensive brand book presentation"""
        prs = Presentation()
        
        # Research fonts
        print(f"🎨 Researching fonts for {company_name}...")
        industry = brand_essence.get("company_profile", {}).get("industry", "technology") if brand_essence else "technology"
        self.researched_fonts = self.font_research_agent.research_fonts(company_name, industry, brand_essence)
        print(f"✅ Selected fonts: {self.researched_fonts['primary_font']} (primary), {self.researched_fonts['secondary_font']} (secondary)")
        
        # Initialize styling system
        self._initialize_styling(identity_data, company_name)
        
        # Create slides
        sections = ["Table of Contents"]
        
        # 1. Title Slide
        self._create_title_slide(prs, company_name, identity_data, brand_essence)
        
        # Build sections list
        if brand_essence:
            if brand_essence.get("company_profile"):
                sections.append("Company Profile")
            if brand_essence.get("market_analysis"):
                sections.append("Market Analysis & Insights")
            if brand_essence.get("brand_positioning"):
                sections.append("Brand Positioning")
        
        sections.extend([
            "Logo Variations",
            "Color Palette", 
            "Typography",
            "Visual & Photography Guidelines",
            "Brand Story & Mission",
            "Brand Voice & Tone",
            "Messaging & Value Propositions",
            "Marketing Copy",
            "Brand Collateral Templates"
        ])
        
        # 2. Table of Contents
        self._create_table_of_contents(prs, sections, identity_data)
        
        # 3. Brand Essence Slides
        if brand_essence:
            if brand_essence.get("company_profile"):
                self._create_company_profile_slide(prs, brand_essence, identity_data)
            if brand_essence.get("market_analysis"):
                self._create_market_analysis_slide(prs, brand_essence, identity_data)
            if brand_essence.get("brand_positioning"):
                self._create_brand_positioning_slide(prs, brand_essence, identity_data)
        
        # 4. Logo Variations
        if identity_data.get("logos"):
            self._create_logo_variations_slide(prs, identity_data["logos"], identity_data)
        
        # 5. Color Palette
        if identity_data.get("palette"):
            self._create_color_palette_slide(prs, identity_data["palette"], identity_data)
        
        # 6. Typography
        self._create_typography_slide(prs, identity_data.get("typography", {}), identity_data)
        
        # 7. Visual & Photography Guidelines
        self._create_visual_guidelines_slide(
            prs,
            identity_data.get("visual_style", ""),
            identity_data.get("photography_style", ""),
            identity_data
        )
        
        # 8. Brand Story & Mission
        story_data = literature_data.get("brand_story", "")
        if story_data:
            self._create_text_slide(prs, "Brand Story & Mission", str(story_data), 100, identity_data)
        
        # 9. Voice & Tone
        voice_data = literature_data.get("voice_tone", "")
        if voice_data:
            self._create_text_slide(prs, "Brand Voice & Tone", voice_data, 80, identity_data)
        
        # 10. Messaging & Value Propositions
        messaging_data = literature_data.get("messaging_arch", "")
        if messaging_data:
            self._create_text_slide(prs, "Messaging & Value Propositions", messaging_data, 80, identity_data)
        
        # 11. Marketing Copy
        marketing_copy = literature_data.get("marketing_copy", {})
        if marketing_copy:
            for channel, copy in marketing_copy.items():
                title = f"Marketing Copy: {channel.replace('_', ' ').title()}"
                self._create_text_slide(prs, title, copy, 70, identity_data)
        
        # 12. Collateral
        collaterals = literature_data.get("collaterals", {})
        if collaterals:
            if isinstance(collaterals, dict):
                for name, desc in collaterals.items():
                    title = f"Collateral: {name.replace('_',' ').title()}"
                    self._create_text_slide(prs, title, desc, 70, identity_data)
            else:
                self._create_text_slide(prs, "Brand Collateral Templates", str(collaterals), 80, identity_data)
        
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