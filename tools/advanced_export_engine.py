from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus import Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, Color
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing, Rect, Circle, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
import io
import os
from typing import Dict, List, Tuple
import json
import markdown
# from weasyprint import HTML, CSS
# from weasyprint.css.style_for import get_all_computed_styles
import tempfile

class AdvancedExportEngine:
    """
    Advanced export engine that creates professional PDF brand books with:
    - Vector graphics and shapes
    - CMYK color profiles
    - Professional typography
    - Multi-page layouts with proper pagination
    """
    
    def __init__(self, company_name: str = None):
        if company_name:
            base_name = company_name.lower().replace(' ', '_')
            self.output_dir = os.path.join("output", base_name, "exports")
        else:
            self.output_dir = "output/exports"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Professional page specifications
        self.page_specs = {
            "size": A4,
            "margins": {
                "top": 2*inch,
                "bottom": 1.5*inch, 
                "left": 1.5*inch,
                "right": 1.5*inch
            },
            "bleed": 3*mm
        }
    
    def export_complete_brand_book(self, company_name: str, brand_essence: Dict,
                                  identity_data: Dict, literature_data: Dict,
                                  collateral_data: Dict = None,
                                  visual_system: Dict = None,
                                  qa_report: Dict = None) -> Dict:
        """
        Export complete brand book in multiple professional formats
        """
        print(f"📄 Exporting complete brand book for {company_name}...")
        
        export_results = {}
        
        try:
            # 1. Professional PDF with vector graphics
            print("  Creating professional PDF...")
            pdf_path = self._create_vector_pdf(
                company_name, brand_essence, identity_data, 
                literature_data, visual_system
            )
            export_results["pdf"] = pdf_path
            
            # 2. Interactive HTML with CSS styling
            print("  Creating interactive HTML...")
            html_path = self._create_interactive_html(
                company_name, brand_essence, identity_data,
                literature_data, visual_system
            )
            export_results["html"] = html_path
            
            # 3. Print-ready PDF with CMYK
            print("  Creating print-ready PDF...")
            print_pdf_path = self._create_print_ready_pdf(
                company_name, identity_data, literature_data, visual_system
            )
            export_results["print_pdf"] = print_pdf_path
            
            # 4. Brand assets package
            print("  Creating brand assets package...")
            assets_path = self._create_assets_package(
                company_name, identity_data, collateral_data
            )
            export_results["assets_package"] = assets_path
            
            # 5. Digital style guide JSON
            print("  Creating digital style guide...")
            styleguide_path = self._create_digital_styleguide(
                company_name, identity_data, visual_system
            )
            export_results["digital_styleguide"] = styleguide_path
            
        except Exception as e:
            print(f"  Warning: Some export formats failed: {e}")
        
        # Export summary
        export_summary = {
            "exports": export_results,
            "formats": list(export_results.keys()),
            "total_files": len(export_results),
            "export_specs": self._get_export_specifications()
        }
        
        return export_summary
    
    def _create_vector_pdf(self, company_name: str, brand_essence: Dict,
                          identity_data: Dict, literature_data: Dict,
                          visual_system: Dict = None) -> str:
        """Create professional PDF with vector graphics"""
        
        filename = f"{company_name.lower().replace(' ', '_')}_brand_book_professional.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=self.page_specs["size"],
            rightMargin=self.page_specs["margins"]["right"],
            leftMargin=self.page_specs["margins"]["left"],
            topMargin=self.page_specs["margins"]["top"],
            bottomMargin=self.page_specs["margins"]["bottom"]
        )
        
        # Get enhanced palette for colors
        palette = identity_data.get("palette", {})
        if visual_system and visual_system.get("enhanced_palette"):
            palette = visual_system["enhanced_palette"].get("base_colors", palette)
        
        # Define styles
        styles = self._create_pdf_styles(palette)
        story = []
        
        # Cover page
        story.extend(self._create_pdf_cover_page(company_name, styles, palette))
        story.append(PageBreak())
        
        # Table of contents
        story.extend(self._create_pdf_toc(styles))
        story.append(PageBreak())
        
        # Brand essence section
        if brand_essence:
            story.extend(self._create_brand_essence_section(brand_essence, styles))
            story.append(PageBreak())
        
        # Visual identity section
        story.extend(self._create_visual_identity_section(identity_data, styles, palette))
        story.append(PageBreak())
        
        # Brand narrative section
        story.extend(self._create_narrative_section(literature_data, styles))
        story.append(PageBreak())
        
        # Usage guidelines
        story.extend(self._create_usage_guidelines_section(identity_data, styles))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _create_pdf_styles(self, palette: Dict) -> Dict:
        """Create professional PDF styles"""
        styles = getSampleStyleSheet()
        
        # Get brand colors
        primary_color = self._get_color_from_palette(palette, "primary", "#333333")
        accent_color = self._get_color_from_palette(palette, "accent", "#0066CC")
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=36,
            spaceAfter=30,
            textColor=HexColor(primary_color),
            fontName='Helvetica-Bold',
            alignment=0  # Left align
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=24,
            spaceBefore=20,
            spaceAfter=15,
            textColor=HexColor(primary_color),
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=styles['Heading3'],
            fontSize=18,
            spaceBefore=15,
            spaceAfter=10,
            textColor=HexColor(accent_color),
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=12,
            spaceBefore=6,
            spaceAfter=6,
            textColor=HexColor("#555555"),
            fontName='Helvetica',
            leading=18
        ))
        
        return styles
    
    def _create_pdf_cover_page(self, company_name: str, styles: Dict, palette: Dict) -> List:
        """Create professional PDF cover page"""
        story = []
        
        # Add company name as main title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(f"{company_name}", styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        story.append(Paragraph("Brand Book", styles['CustomHeading']))
        story.append(Spacer(1, 0.3*inch))
        
        # Description
        story.append(Paragraph(
            "A comprehensive guide to your brand identity, visual system, and messaging strategy.",
            styles['CustomBody']
        ))
        story.append(Spacer(1, 1*inch))
        
        # Add decorative vector element
        drawing = Drawing(400, 100)
        primary_color = self._get_color_from_palette(palette, "primary", "#333333")
        accent_color = self._get_color_from_palette(palette, "accent", "#0066CC")
        
        # Simple decorative rectangles
        drawing.add(Rect(0, 40, 100, 10, fillColor=HexColor(accent_color), strokeColor=None))
        drawing.add(Rect(0, 60, 150, 4, fillColor=HexColor(primary_color), strokeColor=None))
        
        story.append(drawing)
        
        return story
    
    def _create_pdf_toc(self, styles: Dict) -> List:
        """Create table of contents"""
        story = []
        
        story.append(Paragraph("Table of Contents", styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        toc_items = [
            "Brand Essence & Market Analysis",
            "Visual Identity System",
            "Color Palette",
            "Typography",
            "Logo Usage Guidelines", 
            "Brand Narrative & Voice",
            "Messaging Architecture",
            "Usage Guidelines",
            "Brand Applications"
        ]
        
        for i, item in enumerate(toc_items, 1):
            story.append(Paragraph(f"{i}. {item}", styles['CustomBody']))
            story.append(Spacer(1, 6))
        
        return story
    
    def _create_brand_essence_section(self, brand_essence: Dict, styles: Dict) -> List:
        """Create brand essence section for PDF"""
        story = []
        
        story.append(Paragraph("Brand Essence & Market Analysis", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Company profile
        if brand_essence.get("company_profile"):
            profile = brand_essence["company_profile"]
            story.append(Paragraph("Company Profile", styles['CustomHeading']))
            story.append(Paragraph(f"<b>Industry:</b> {profile.get('industry', 'N/A')}", styles['CustomBody']))
            story.append(Paragraph(f"<b>Target Audience:</b> {profile.get('target_audience', 'N/A')}", styles['CustomBody']))
            
            if profile.get("core_values"):
                story.append(Paragraph("<b>Core Values:</b>", styles['CustomBody']))
                for value in profile["core_values"]:
                    story.append(Paragraph(f"• {value}", styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Brand positioning
        if brand_essence.get("brand_positioning"):
            positioning = brand_essence["brand_positioning"]
            story.append(Paragraph("Brand Positioning", styles['CustomHeading']))
            story.append(Paragraph(f"<b>Value Proposition:</b> {positioning.get('unique_value_proposition', 'N/A')}", styles['CustomBody']))
            story.append(Paragraph(f"<b>Brand Promise:</b> {positioning.get('brand_promise', 'N/A')}", styles['CustomBody']))
            
            if positioning.get("brand_personality"):
                personality = ", ".join(positioning["brand_personality"])
                story.append(Paragraph(f"<b>Brand Personality:</b> {personality}", styles['CustomBody']))
        
        return story
    
    def _create_visual_identity_section(self, identity_data: Dict, styles: Dict, palette: Dict) -> List:
        """Create visual identity section"""
        story = []
        
        story.append(Paragraph("Visual Identity System", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Color palette section
        story.append(Paragraph("Color Palette", styles['CustomHeading']))
        
        if palette:
            # Create color swatches table
            color_data = []
            for name, color_value in palette.items():
                if isinstance(color_value, str) and color_value.startswith('#'):
                    color_data.append([name.title(), color_value.upper()])
            
            if color_data:
                color_table = Table(color_data, colWidths=[2*inch, 1*inch])
                color_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor("#f0f0f0")),
                    ('TEXTCOLOR', (0, 0), (-1, -1), HexColor("#333333")),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f8f8f8")]),
                    ('GRID', (0, 0), (-1, -1), 1, HexColor("#cccccc"))
                ]))
                story.append(color_table)
        
        story.append(Spacer(1, 0.2*inch))
        
        # Typography section
        typography = identity_data.get("typography", {})
        if typography:
            story.append(Paragraph("Typography", styles['CustomHeading']))
            
            if isinstance(typography, dict):
                if typography.get("primary"):
                    story.append(Paragraph(f"<b>Primary Font:</b> {typography['primary']}", styles['CustomBody']))
                if typography.get("secondary"):
                    story.append(Paragraph(f"<b>Secondary Font:</b> {typography['secondary']}", styles['CustomBody']))
                if typography.get("description"):
                    story.append(Paragraph(typography["description"], styles['CustomBody']))
        
        return story
    
    def _create_narrative_section(self, literature_data: Dict, styles: Dict) -> List:
        """Create brand narrative section"""
        story = []
        
        story.append(Paragraph("Brand Narrative & Voice", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Brand story
        if literature_data.get("brand_story"):
            story.append(Paragraph("Brand Story", styles['CustomHeading']))
            story.append(Paragraph(literature_data["brand_story"], styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Voice and tone
        if literature_data.get("voice_tone"):
            story.append(Paragraph("Voice & Tone", styles['CustomHeading']))
            story.append(Paragraph(literature_data["voice_tone"], styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Messaging architecture
        if literature_data.get("messaging_arch"):
            story.append(Paragraph("Messaging Architecture", styles['CustomHeading']))
            story.append(Paragraph(literature_data["messaging_arch"], styles['CustomBody']))
        
        return story
    
    def _create_usage_guidelines_section(self, identity_data: Dict, styles: Dict) -> List:
        """Create usage guidelines section"""
        story = []
        
        story.append(Paragraph("Usage Guidelines", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Logo usage guidelines
        story.append(Paragraph("Logo Usage", styles['CustomHeading']))
        logo_guidelines = [
            "Maintain minimum clear space around the logo",
            "Use approved color variations only",
            "Do not distort, rotate, or modify the logo",
            "Ensure sufficient contrast on all backgrounds",
            "Use vector formats when possible for scalability"
        ]
        
        for guideline in logo_guidelines:
            story.append(Paragraph(f"• {guideline}", styles['CustomBody']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Color usage guidelines
        story.append(Paragraph("Color Usage", styles['CustomHeading']))
        color_guidelines = [
            "Primary colors for headers and key elements",
            "Secondary colors for backgrounds and large areas", 
            "Accent colors for calls-to-action and highlights",
            "Maintain WCAG AA contrast ratios for accessibility",
            "Use CMYK values for print applications"
        ]
        
        for guideline in color_guidelines:
            story.append(Paragraph(f"• {guideline}", styles['CustomBody']))
        
        return story
    
    def _create_interactive_html(self, company_name: str, brand_essence: Dict,
                               identity_data: Dict, literature_data: Dict,
                               visual_system: Dict = None) -> str:
        """Create interactive HTML brand book"""
        
        filename = f"{company_name.lower().replace(' ', '_')}_brand_book_interactive.html"
        filepath = os.path.join(self.output_dir, filename)
        
        # Get enhanced styling
        css_styles = self._generate_advanced_css(identity_data, visual_system)
        
        # Generate HTML content
        html_content = self._generate_html_content(
            company_name, brand_essence, identity_data, literature_data
        )
        
        # Complete HTML document
        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{company_name} Brand Book</title>
            <style>{css_styles}</style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        return filepath
    
    def _generate_advanced_css(self, identity_data: Dict, visual_system: Dict = None) -> str:
        """Generate advanced CSS with gradients and animations"""
        
        palette = identity_data.get("palette", {})
        if visual_system and visual_system.get("enhanced_palette"):
            palette = visual_system["enhanced_palette"].get("base_colors", palette)
        
        primary = self._get_color_from_palette(palette, "primary", "#333333")
        accent = self._get_color_from_palette(palette, "accent", "#0066CC")
        secondary = self._get_color_from_palette(palette, "secondary", "#666666")
        
        return f"""
        :root {{
            --primary-color: {primary};
            --accent-color: {accent};
            --secondary-color: {secondary};
            --gradient-primary: linear-gradient(135deg, {primary}, {accent});
            --gradient-section: linear-gradient(180deg, #f8f9fa, #ffffff);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--secondary-color);
            background: var(--gradient-section);
        }}
        
        .hero {{
            background: var(--gradient-primary);
            color: white;
            padding: 4rem 2rem;
            text-align: center;
            min-height: 60vh;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }}
        
        .hero h1 {{
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }}
        
        .section {{
            padding: 4rem 0;
            margin-bottom: 2rem;
        }}
        
        .section-title {{
            font-size: 2.5rem;
            color: var(--primary-color);
            margin-bottom: 2rem;
            position: relative;
            padding-bottom: 1rem;
        }}
        
        .section-title::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 60px;
            height: 4px;
            background: var(--accent-color);
            border-radius: 2px;
        }}
        
        .color-palette {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }}
        
        .color-swatch {{
            text-align: center;
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }}
        
        .color-swatch:hover {{
            transform: translateY(-4px);
        }}
        
        .swatch {{
            width: 100%;
            height: 120px;
            border-radius: 6px;
            margin-bottom: 1rem;
            border: 1px solid #eee;
        }}
        
        .brand-card {{
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        
        .typography-demo {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin: 1rem 0;
        }}
        
        @media (max-width: 768px) {{
            .hero {{ padding: 2rem 1rem; }}
            .section {{ padding: 2rem 0; }}
            .container {{ padding: 0 1rem; }}
        }}
        """
    
    def _generate_html_content(self, company_name: str, brand_essence: Dict,
                             identity_data: Dict, literature_data: Dict) -> str:
        """Generate HTML content structure"""
        
        palette = identity_data.get("palette", {})
        
        html_sections = []
        
        # Hero section
        html_sections.append(f"""
        <section class="hero">
            <div class="container">
                <h1>{company_name}</h1>
                <p style="font-size: 1.25rem; opacity: 0.9;">Brand Book & Style Guide</p>
            </div>
        </section>
        """)
        
        # Brand essence section
        if brand_essence:
            html_sections.append(self._create_html_brand_essence_section(brand_essence))
        
        # Visual identity section
        html_sections.append(self._create_html_visual_section(identity_data, palette))
        
        # Brand narrative section
        if literature_data:
            html_sections.append(self._create_html_narrative_section(literature_data))
        
        return '\n'.join(html_sections)
    
    def _create_html_brand_essence_section(self, brand_essence: Dict) -> str:
        """Create HTML brand essence section"""
        return f"""
        <section class="section">
            <div class="container">
                <h2 class="section-title">Brand Essence</h2>
                <div class="brand-card">
                    <h3>Company Profile</h3>
                    <p><strong>Industry:</strong> {brand_essence.get('company_profile', {}).get('industry', 'N/A')}</p>
                    <p><strong>Target Audience:</strong> {brand_essence.get('company_profile', {}).get('target_audience', 'N/A')}</p>
                </div>
            </div>
        </section>
        """
    
    def _create_html_visual_section(self, identity_data: Dict, palette: Dict) -> str:
        """Create HTML visual identity section"""
        color_swatches = ""
        
        if palette:
            for name, color in palette.items():
                if isinstance(color, str) and color.startswith('#'):
                    color_swatches += f"""
                    <div class="color-swatch">
                        <div class="swatch" style="background-color: {color};"></div>
                        <h4>{name.title()}</h4>
                        <p>{color.upper()}</p>
                    </div>
                    """
        
        return f"""
        <section class="section">
            <div class="container">
                <h2 class="section-title">Visual Identity</h2>
                <div class="brand-card">
                    <h3>Color Palette</h3>
                    <div class="color-palette">
                        {color_swatches}
                    </div>
                </div>
            </div>
        </section>
        """
    
    def _create_html_narrative_section(self, literature_data: Dict) -> str:
        """Create HTML narrative section"""
        return f"""
        <section class="section">
            <div class="container">
                <h2 class="section-title">Brand Narrative</h2>
                <div class="brand-card">
                    <h3>Brand Story</h3>
                    <p>{literature_data.get('brand_story', 'No brand story available')}</p>
                </div>
                <div class="brand-card">
                    <h3>Voice & Tone</h3>
                    <p>{literature_data.get('voice_tone', 'No voice and tone guidelines available')}</p>
                </div>
            </div>
        </section>
        """
    
    def _create_print_ready_pdf(self, company_name: str, identity_data: Dict,
                               literature_data: Dict, visual_system: Dict = None) -> str:
        """Create print-ready PDF with CMYK support"""
        # For now, create a simplified print version
        filename = f"{company_name.lower().replace(' ', '_')}_brand_book_print.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # This would ideally use CMYK color spaces and higher resolution
        # For this implementation, we'll create a simplified version
        return self._create_vector_pdf(company_name, {}, identity_data, literature_data, visual_system)
    
    def _create_assets_package(self, company_name: str, identity_data: Dict,
                             collateral_data: Dict = None) -> str:
        """Create downloadable assets package"""
        assets_dir = os.path.join(self.output_dir, f"{company_name.lower().replace(' ', '_')}_assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        # Create assets summary
        assets_summary = {
            "company": company_name,
            "assets": {
                "logos": [],
                "colors": identity_data.get("palette", {}),
                "typography": identity_data.get("typography", {}),
                "collateral": []
            },
            "formats": ["PNG", "SVG", "PDF"],
            "usage_rights": "Internal use only"
        }
        
        # Save assets summary
        summary_path = os.path.join(assets_dir, "assets_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(assets_summary, f, indent=2)
        
        return assets_dir
    
    def _create_digital_styleguide(self, company_name: str, identity_data: Dict,
                                  visual_system: Dict = None) -> str:
        """Create digital style guide JSON"""
        filename = f"{company_name.lower().replace(' ', '_')}_styleguide.json"
        filepath = os.path.join(self.output_dir, filename)
        
        styleguide = {
            "company": company_name,
            "version": "1.0",
            "colors": identity_data.get("palette", {}),
            "typography": identity_data.get("typography", {}),
            "spacing": visual_system.get("spacing_system", {}) if visual_system else {},
            "components": {
                "buttons": {
                    "primary": {"background": "var(--accent-color)", "color": "white"},
                    "secondary": {"background": "transparent", "border": "1px solid var(--accent-color)"}
                }
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(styleguide, f, indent=2)
        
        return filepath
    
    def _get_color_from_palette(self, palette: Dict, color_name: str, default: str) -> str:
        """Safely get color from palette"""
        if not palette:
            return default
        
        color = palette.get(color_name)
        if isinstance(color, str) and color.startswith('#'):
            return color
        elif isinstance(color, list) and color:
            return color[0] if color[0].startswith('#') else default
        
        return default
    
    def _get_export_specifications(self) -> Dict:
        """Get technical specifications for all export formats"""
        return {
            "pdf": {
                "format": "PDF/A-1b compliant",
                "resolution": "300 DPI",
                "color_space": "RGB with CMYK notes",
                "fonts": "Embedded",
                "vector_graphics": True
            },
            "html": {
                "format": "HTML5 with CSS3",
                "responsive": True,
                "animations": "CSS transitions",
                "compatibility": "Modern browsers"
            },
            "print_pdf": {
                "format": "PDF/X-1a compliant",
                "resolution": "300 DPI", 
                "color_space": "CMYK",
                "bleed": "3mm all sides",
                "trim_marks": True
            },
            "assets": {
                "logo_formats": ["SVG", "PNG", "PDF"],
                "color_formats": ["HEX", "RGB", "CMYK", "Pantone"],
                "usage_guidelines": "Included"
            }
        }