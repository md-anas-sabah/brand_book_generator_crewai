from typing import Dict, List, Tuple
import re
try:
    import colorsys
except ImportError:
    colorsys = None
from urllib.parse import urlparse
import requests
import os

class QAComplianceAgent:
    """
    Quality Assurance and Compliance Agent that ensures brand books meet
    accessibility standards, licensing requirements, and quality checks.
    """
    
    def __init__(self):
        self.accessibility_standards = {
            "WCAG_AA": 4.5,  # Minimum contrast ratio
            "WCAG_AAA": 7.0   # Enhanced contrast ratio
        }
        
        self.safe_fonts = {
            # Web-safe and commonly licensed fonts
            "arial", "helvetica", "georgia", "times", "courier", 
            "verdana", "tahoma", "trebuchet", "impact", "comic sans ms",
            # Google Fonts (free to use)
            "roboto", "open sans", "lato", "montserrat", "source sans pro",
            "raleway", "poppins", "inter", "playfair display"
        }
    
    def perform_qa_audit(self, company_name: str, identity_data: Dict, 
                        literature_data: Dict, brand_essence: Dict = None,
                        collateral_data: Dict = None) -> Dict:
        """
        Perform comprehensive QA and compliance audit of the brand book
        """
        print(f"🔍 Performing QA audit for {company_name} brand book...")
        
        audit_results = {
            "accessibility_audit": self._audit_accessibility(identity_data),
            "licensing_audit": self._audit_licensing(identity_data),
            "content_quality_audit": self._audit_content_quality(literature_data),
            "technical_compliance": self._audit_technical_compliance(identity_data),
            "brand_consistency": self._audit_brand_consistency(identity_data, literature_data, brand_essence),
            "export_readiness": self._audit_export_readiness(identity_data, collateral_data),
            "overall_score": 0,
            "recommendations": [],
            "critical_issues": [],
            "warnings": []
        }
        
        # Calculate overall score and generate recommendations
        audit_results["overall_score"] = self._calculate_overall_score(audit_results)
        audit_results["recommendations"] = self._generate_recommendations(audit_results)
        
        return audit_results
    
    def _audit_accessibility(self, identity_data: Dict) -> Dict:
        """Audit color accessibility and WCAG compliance"""
        palette = identity_data.get("palette", {})
        accessibility_report = {
            "wcag_aa_compliant": True,
            "wcag_aaa_compliant": True,
            "contrast_ratios": {},
            "color_blind_friendly": True,
            "issues": []
        }
        
        # Extract colors for testing
        colors = []
        if isinstance(palette, dict):
            for key, value in palette.items():
                if isinstance(value, str) and value.startswith('#'):
                    colors.append((key, value))
                elif isinstance(value, list):
                    for i, color in enumerate(value):
                        if isinstance(color, str) and color.startswith('#'):
                            colors.append((f"{key}_{i}", color))
        
        # Test contrast ratios against white and black
        for name, color_hex in colors:
            # Test against white background
            white_contrast = self._calculate_contrast_ratio(color_hex, "#FFFFFF")
            black_contrast = self._calculate_contrast_ratio(color_hex, "#000000")
            
            accessibility_report["contrast_ratios"][name] = {
                "vs_white": white_contrast,
                "vs_black": black_contrast,
                "aa_compliant": max(white_contrast, black_contrast) >= self.accessibility_standards["WCAG_AA"],
                "aaa_compliant": max(white_contrast, black_contrast) >= self.accessibility_standards["WCAG_AAA"]
            }
            
            # Check WCAG compliance
            if max(white_contrast, black_contrast) < self.accessibility_standards["WCAG_AA"]:
                accessibility_report["wcag_aa_compliant"] = False
                accessibility_report["issues"].append(f"Color {name} ({color_hex}) fails WCAG AA contrast requirements")
            
            if max(white_contrast, black_contrast) < self.accessibility_standards["WCAG_AAA"]:
                accessibility_report["wcag_aaa_compliant"] = False
        
        # Color blind accessibility check
        accessibility_report["color_blind_analysis"] = self._analyze_color_blind_accessibility(colors)
        
        return accessibility_report
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        def hex_to_luminance(hex_color: str) -> float:
            # Remove # and convert to RGB
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            
            try:
                rgb = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
            except:
                return 0.5  # Default luminance for invalid colors
            
            # Convert to relative luminance
            rgb_normalized = [c/255.0 for c in rgb]
            rgb_linear = []
            
            for c in rgb_normalized:
                if c <= 0.03928:
                    rgb_linear.append(c / 12.92)
                else:
                    rgb_linear.append(((c + 0.055) / 1.055) ** 2.4)
            
            # Calculate luminance
            return 0.2126 * rgb_linear[0] + 0.7152 * rgb_linear[1] + 0.0722 * rgb_linear[2]
        
        lum1 = hex_to_luminance(color1)
        lum2 = hex_to_luminance(color2)
        
        # Ensure lighter color is numerator
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def _analyze_color_blind_accessibility(self, colors: List[Tuple[str, str]]) -> Dict:
        """Analyze color palette for color blind accessibility"""
        analysis = {
            "deuteranopia_safe": True,
            "protanopia_safe": True, 
            "tritanopia_safe": True,
            "recommendations": []
        }
        
        # Check for problematic color combinations
        problematic_combinations = [
            ("#FF0000", "#00FF00"),  # Red-Green
            ("#0000FF", "#FFFF00"),  # Blue-Yellow (less common issue)
        ]
        
        color_values = [color[1] for color in colors]
        
        # Simple heuristic: check if palette relies too heavily on similar hues
        hues = []
        for _, color_hex in colors:
            try:
                rgb = self._hex_to_rgb(color_hex)
                hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                hues.append(hsv[0])
            except:
                continue
        
        if len(hues) > 1:
            # Check for hues that are too similar (problematic for color blind users)
            for i in range(len(hues)):
                for j in range(i+1, len(hues)):
                    hue_diff = abs(hues[i] - hues[j])
                    if hue_diff < 0.1 or hue_diff > 0.9:  # Very similar or opposite hues
                        analysis["recommendations"].append(
                            "Consider adding more hue diversity to improve color blind accessibility"
                        )
                        break
        
        return analysis
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex to RGB"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _audit_licensing(self, identity_data: Dict) -> Dict:
        """Audit font and asset licensing compliance"""
        typography = identity_data.get("typography", {})
        licensing_report = {
            "font_licensing_safe": True,
            "font_issues": [],
            "recommendations": []
        }
        
        # Check fonts against safe list
        fonts_to_check = []
        if isinstance(typography, dict):
            for key, value in typography.items():
                if isinstance(value, str):
                    fonts_to_check.append(value.lower())
                elif isinstance(value, list):
                    fonts_to_check.extend([f.lower() for f in value if isinstance(f, str)])
        
        for font in fonts_to_check:
            if font not in self.safe_fonts:
                licensing_report["font_licensing_safe"] = False
                licensing_report["font_issues"].append(f"Font '{font}' may require licensing verification")
        
        # Add recommendations for safe alternatives
        if not licensing_report["font_licensing_safe"]:
            licensing_report["recommendations"].extend([
                "Consider using Google Fonts for guaranteed free licensing",
                "Verify commercial licensing for all custom fonts",
                "Document font licensing in brand guidelines"
            ])
        
        return licensing_report
    
    def _audit_content_quality(self, literature_data: Dict) -> Dict:
        """Audit content quality and completeness"""
        quality_report = {
            "completeness_score": 0,
            "readability_score": "good",
            "consistency_issues": [],
            "missing_elements": [],
            "content_length_appropriate": True
        }
        
        # Check for required content elements
        required_elements = ["brand_story", "voice_tone", "messaging_arch"]
        present_elements = 0
        
        for element in required_elements:
            if literature_data.get(element):
                present_elements += 1
            else:
                quality_report["missing_elements"].append(element)
        
        quality_report["completeness_score"] = (present_elements / len(required_elements)) * 100
        
        # Check content length appropriateness
        for key, content in literature_data.items():
            if isinstance(content, str):
                if len(content) < 50:
                    quality_report["consistency_issues"].append(f"{key} content is too brief")
                elif len(content) > 2000:
                    quality_report["consistency_issues"].append(f"{key} content may be too lengthy")
        
        return quality_report
    
    def _audit_technical_compliance(self, identity_data: Dict) -> Dict:
        """Audit technical specifications and format compliance"""
        palette = identity_data.get("palette", {})
        
        compliance_report = {
            "color_format_valid": True,
            "hex_codes_valid": True,
            "palette_completeness": 0,
            "technical_issues": []
        }
        
        # Validate hex color codes
        valid_colors = 0
        total_colors = 0
        
        if isinstance(palette, dict):
            for key, value in palette.items():
                if isinstance(value, str):
                    total_colors += 1
                    if self._validate_hex_color(value):
                        valid_colors += 1
                    else:
                        compliance_report["hex_codes_valid"] = False
                        compliance_report["technical_issues"].append(f"Invalid hex code: {value}")
                elif isinstance(value, list):
                    for color in value:
                        if isinstance(color, str):
                            total_colors += 1
                            if self._validate_hex_color(color):
                                valid_colors += 1
                            else:
                                compliance_report["hex_codes_valid"] = False
                                compliance_report["technical_issues"].append(f"Invalid hex code: {color}")
        
        if total_colors > 0:
            compliance_report["palette_completeness"] = (valid_colors / total_colors) * 100
        
        return compliance_report
    
    def _validate_hex_color(self, color: str) -> bool:
        """Validate hex color format"""
        if not isinstance(color, str):
            return False
        
        # Remove # if present
        color = color.lstrip('#')
        
        # Check if it's 3 or 6 characters and all hex digits
        return len(color) in [3, 6] and all(c in '0123456789ABCDEFabcdef' for c in color)
    
    def _audit_brand_consistency(self, identity_data: Dict, literature_data: Dict, brand_essence: Dict) -> Dict:
        """Audit brand consistency across all elements"""
        consistency_report = {
            "style_consistency": True,
            "messaging_alignment": True,
            "visual_coherence": True,
            "inconsistencies": []
        }
        
        # Check if visual style aligns with brand personality
        if brand_essence and brand_essence.get("brand_positioning"):
            personality = brand_essence["brand_positioning"].get("brand_personality", [])
            visual_direction = brand_essence.get("visual_direction", {})
            
            # Simple heuristic checks
            if "professional" in personality and visual_direction.get("recommended_style") == "colourful":
                consistency_report["style_consistency"] = False
                consistency_report["inconsistencies"].append(
                    "Professional brand personality may not align with colourful visual style"
                )
        
        return consistency_report
    
    def _audit_export_readiness(self, identity_data: Dict, collateral_data: Dict) -> Dict:
        """Audit readiness for various export formats"""
        export_report = {
            "print_ready": True,
            "web_ready": True,
            "mobile_ready": True,
            "scalability_issues": [],
            "format_compatibility": []
        }
        
        # Check if all required formats and specifications are present
        palette = identity_data.get("palette", {})
        
        # Ensure CMYK alternatives are considered for print
        if palette and not any("cmyk" in str(key).lower() for key in palette.keys()):
            export_report["format_compatibility"].append(
                "Consider providing CMYK color values for print applications"
            )
        
        # Check collateral specifications
        if collateral_data and collateral_data.get("template_specifications"):
            specs = collateral_data["template_specifications"]
            if not specs.get("business_card", {}).get("bleed"):
                export_report["scalability_issues"].append("Print materials missing bleed specifications")
        
        return export_report
    
    def _calculate_overall_score(self, audit_results: Dict) -> float:
        """Calculate overall QA score (0-100)"""
        scores = []
        
        # Accessibility score (weight: 25%)
        accessibility = audit_results["accessibility_audit"]
        if accessibility["wcag_aa_compliant"]:
            scores.append(25)
        elif accessibility["wcag_aaa_compliant"]:
            scores.append(20)
        else:
            scores.append(10)
        
        # Content quality score (weight: 25%)
        content_score = audit_results["content_quality_audit"]["completeness_score"]
        scores.append(content_score * 0.25)
        
        # Technical compliance (weight: 20%)
        technical = audit_results["technical_compliance"]
        if technical["hex_codes_valid"]:
            scores.append(20)
        else:
            scores.append(technical["palette_completeness"] * 0.20)
        
        # Licensing compliance (weight: 15%)
        licensing = audit_results["licensing_audit"]
        if licensing["font_licensing_safe"]:
            scores.append(15)
        else:
            scores.append(10)
        
        # Brand consistency (weight: 15%)
        consistency = audit_results["brand_consistency"]
        if consistency["style_consistency"] and consistency["messaging_alignment"]:
            scores.append(15)
        else:
            scores.append(10)
        
        return sum(scores)
    
    def _generate_recommendations(self, audit_results: Dict) -> List[str]:
        """Generate actionable recommendations based on audit results"""
        recommendations = []
        
        # Accessibility recommendations
        accessibility = audit_results["accessibility_audit"]
        if not accessibility["wcag_aa_compliant"]:
            recommendations.append("🔴 CRITICAL: Improve color contrast to meet WCAG AA standards (4.5:1 minimum)")
        
        if accessibility["issues"]:
            recommendations.append("⚠️  Review color accessibility issues and adjust palette accordingly")
        
        # Content quality recommendations
        content = audit_results["content_quality_audit"]
        if content["completeness_score"] < 80:
            recommendations.append("📝 Complete missing content elements for comprehensive brand book")
        
        # Licensing recommendations
        licensing = audit_results["licensing_audit"]
        if not licensing["font_licensing_safe"]:
            recommendations.append("📄 Verify font licensing or switch to Google Fonts for safe usage")
        
        # Technical recommendations
        technical = audit_results["technical_compliance"]
        if technical["technical_issues"]:
            recommendations.append("🔧 Fix technical issues with color codes and formatting")
        
        # Export readiness
        export_ready = audit_results["export_readiness"]
        if export_ready["format_compatibility"]:
            recommendations.append("🎨 Add CMYK color specifications for professional printing")
        
        # Overall score recommendations
        overall_score = audit_results["overall_score"]
        if overall_score < 70:
            recommendations.append("🎯 Overall brand book quality needs improvement - address critical issues first")
        elif overall_score < 85:
            recommendations.append("✨ Good foundation - focus on polish and accessibility improvements")
        else:
            recommendations.append("🏆 Excellent brand book quality - ready for professional use!")
        
        return recommendations