from crewai import Crew, Agent, Task, Process
from agents.brand_strategist_agent import BrandStrategistAgent
from agents.identity_agent import IdentityAgent
from agents.literature_agent import LiteratureAgent
from agents.collateral_agent import CollateralAgent
from agents.qa_compliance_agent import QAComplianceAgent
from tools.pptx_generator import PPTXGenerator
from tools.visual_enhancement import VisualEnhancementEngine
from tools.advanced_export_engine import AdvancedExportEngine
from typing import Dict
import os
import markdown2
import json

def dict_to_markdown(d, title=None):
    md = ""
    if title:
        md += f"# {title}\n\n"
    for k, v in d.items():
        if isinstance(v, dict):
            md += f"## {k}\n\n"
            md += dict_to_markdown(v)
        elif isinstance(v, list):
            md += f"**{k}**:\n"
            for item in v:
                md += f"- {item}\n"
            md += "\n"
        else:
            md += f"**{k}**: {v}\n\n"
    return md

class BrandBookOrchestrator:
    """
    World-class brand book orchestrator that coordinates multiple specialized agents
    to create research-driven, professional brand books with advanced features.
    """
    
    def __init__(self):
        # Initialize all agents
        self.brand_strategist = BrandStrategistAgent()
        self.identity_agent = IdentityAgent()
        self.literature_agent = LiteratureAgent()
        self.collateral_agent = None  # Initialize later with company name
        self.qa_agent = QAComplianceAgent()
        self.visual_engine = VisualEnhancementEngine()
        self.export_engine = None  # Initialize later with company name
        self.pptx_generator = PPTXGenerator()
        
        # Setup CrewAI agents for coordination
        self.strategist_crew_agent = Agent(
            role='Brand Strategist',
            goal='Conduct deep research and create comprehensive Brand Essence document',
            backstory='Expert brand strategist with deep knowledge of market research and competitor analysis',
            verbose=True,
            allow_delegation=False
        )
        
        self.creative_director = Agent(
            role='Creative Director',
            goal='Transform brand strategy into compelling visual identity with research-driven design',
            backstory='Visionary creative director specializing in research-informed brand identity design',
            verbose=True,
            allow_delegation=False
        )
        
        self.copywriter = Agent(
            role='Master Copywriter',
            goal='Craft compelling brand narrative and messaging based on strategic insights',
            backstory='Award-winning copywriter with expertise in positioning-driven brand storytelling',
            verbose=True,
            allow_delegation=False
        )
        
        self.collateral_designer = Agent(
            role='Collateral Designer',
            goal='Create professional mockups and brand application templates',
            backstory='Expert designer specializing in brand collateral and template creation',
            verbose=True,
            allow_delegation=False
        )
        
        self.qa_specialist = Agent(
            role='QA & Compliance Specialist', 
            goal='Ensure accessibility, licensing, and professional quality standards',
            backstory='Quality assurance expert with deep knowledge of accessibility and brand compliance',
            verbose=True,
            allow_delegation=False
        )
    
    def run(self):
        print("=== World-Class Brand Book Creator ===")
        print("🚀 Creating research-driven, professional brand books with AI creative team")
        print("📊 Includes: Web research • Dynamic design • QA compliance • Advanced exports\n")
        
        # Gather comprehensive user input
        company_name = input("Company name: ").strip()
        industry = input("Industry: ").strip()
        values = input("Company values (comma-separated): ").strip()
        audience = input("Target audience: ").strip()
        logo_style = input("Logo/brand style (minimalistic, modern, elegant, etc): ").strip()
        
        print(f"\n🎯 Creating comprehensive brand book for {company_name}...")
        print("=" * 80)
        
        # Initialize export engine and collateral agent with company name for folder structure
        self.export_engine = AdvancedExportEngine(company_name)
        self.collateral_agent = CollateralAgent(company_name)

        # Phase 1: Strategic Research & Brand Essence Creation
        print("\n🔍 PHASE 1: Strategic Research & Brand Essence Creation")
        print("-" * 60)
        
        brand_essence = self.brand_strategist.create_brand_essence(
            company_name, industry, values, audience
        )
        
        self._display_phase_results("Brand Essence & Market Analysis", brand_essence)
        
        # Intelligent auto-approval checkpoint
        if not self._intelligent_approval("brand essence", brand_essence):
            print("\n❌ Brand essence quality issues detected. Process stopped.")
            return

        # Phase 2: Visual Identity & Creative Direction
        print("\n🎨 PHASE 2: Visual Identity & Creative Direction")
        print("-" * 60)
        
        identity_data = self.identity_agent.create_identity(
            company_name, industry, values, audience, logo_style, brand_essence
        )
        
        # Enhance visual system
        print("  Applying visual enhancements...")
        visual_system = self.visual_engine.enhance_brand_book_visuals(
            identity_data.get("palette", {}), 
            identity_data.get("typography", {}),
            company_name, 
            logo_style
        )
        
        self._display_phase_results("Enhanced Visual Identity System", {
            "identity": identity_data,
            "visual_enhancements": visual_system
        })
        
        # Intelligent auto-approval checkpoint
        if not self._intelligent_approval("visual identity", {"identity": identity_data, "visual_system": visual_system}):
            print("\n❌ Visual identity quality issues detected. Process stopped.")
            return

        # Phase 3: Brand Narrative & Messaging
        print("\n✍️ PHASE 3: Brand Narrative & Messaging")
        print("-" * 60)
        
        literature_data = self.literature_agent.create_literature(
            company_name, industry, values, audience, brand_essence
        )
        
        self._display_phase_results("Brand Narrative & Messaging", literature_data)
        
        # Intelligent auto-approval checkpoint
        if not self._intelligent_approval("brand narrative", literature_data):
            print("\n❌ Brand narrative quality issues detected. Process stopped.")
            return

        # Phase 4: Collateral Creation
        print("\n🎭 PHASE 4: Brand Collateral & Templates")
        print("-" * 60)
        
        collateral_data = self.collateral_agent.create_collateral_suite(
            company_name, identity_data, literature_data, brand_essence
        )
        
        self._display_phase_results("Brand Collateral Suite", collateral_data)
        
        # Intelligent auto-approval checkpoint
        if not self._intelligent_approval("brand collateral", collateral_data):
            print("\n❌ Brand collateral quality issues detected. Process stopped.")
            return

        # Phase 5: Quality Assurance & Compliance
        print("\n🔍 PHASE 5: Quality Assurance & Compliance Audit")
        print("-" * 60)
        
        qa_report = self.qa_agent.perform_qa_audit(
            company_name, identity_data, literature_data, brand_essence, collateral_data
        )
        
        self._display_qa_results(qa_report)
        
        # Handle QA issues if any
        if qa_report.get("overall_score", 0) < 50:
            print("\n❌ QA Score critically low - Process stopped for quality issues.")
            print("🔧 Recommendations to fix:")
            for rec in qa_report.get("recommendations", [])[:5]:
                print(f"  • {rec}")
            return
        elif qa_report.get("overall_score", 0) < 70:
            print("\n⚠️ QA Score below 70 - Will include improvement recommendations in final output")
            print("🔄 Continuing with current quality level...")

        # Phase 6: Advanced Export & Final Assembly  
        print("\n📦 PHASE 6: Advanced Export & Final Assembly")
        print("-" * 60)
        
        # Save comprehensive outputs
        self._save_comprehensive_outputs(
            company_name, brand_essence, identity_data, literature_data, 
            collateral_data, visual_system, qa_report
        )
        
        # Advanced exports
        print("  Creating advanced export formats...")
        export_results = self.export_engine.export_complete_brand_book(
            company_name, brand_essence, identity_data, literature_data,
            collateral_data, visual_system, qa_report
        )
        
        # Enhanced PowerPoint
        print("  Generating professional PowerPoint presentation...")
        enhanced_pptx_path = self._create_professional_pptx(
            company_name, identity_data, literature_data, brand_essence, visual_system
        )
        
        # Final summary
        self._display_final_summary(company_name, export_results, enhanced_pptx_path, qa_report)
        
        print("\n🏆 WORLD-CLASS BRAND BOOK CREATION COMPLETE!")
        print("=" * 80)
    
    def _display_phase_results(self, phase_name: str, data: dict, max_preview: int = 300):
        """Display phase results with better formatting"""
        print(f"\n📋 {phase_name.upper()} - PREVIEW")
        print("=" * 50)
        
        if isinstance(data, dict):
            # Show key insights from each section
            for key, value in list(data.items())[:3]:  # Show first 3 items
                print(f"\n• {key.replace('_', ' ').title()}:")
                if isinstance(value, dict) and value:
                    first_item = next(iter(value.items()))
                    preview_text = str(first_item[1])[:max_preview]
                    if len(str(first_item[1])) > max_preview:
                        preview_text += "..."
                    print(f"  {first_item[0]}: {preview_text}")
                elif isinstance(value, list) and value:
                    print(f"  {value[0]} (+ {len(value)-1} more items)")
                else:
                    preview_text = str(value)[:max_preview]
                    if len(str(value)) > max_preview:
                        preview_text += "..."
                    print(f"  {preview_text}")
        else:
            preview_text = str(data)[:max_preview]
            if len(str(data)) > max_preview:
                preview_text += "..."
            print(preview_text)
        
        print("\n" + "=" * 50)
    
    def _display_qa_results(self, qa_report: Dict):
        """Display QA results with score and recommendations"""
        score = qa_report.get("overall_score", 0)
        
        print(f"\n📊 QUALITY ASSURANCE REPORT")
        print("=" * 50)
        print(f"Overall Score: {score:.1f}/100")
        
        # Score interpretation
        if score >= 90:
            print("🏆 EXCELLENT - Professional grade quality")
        elif score >= 80:
            print("✅ VERY GOOD - Minor improvements recommended")
        elif score >= 70:
            print("⚠️ GOOD - Some improvements needed")
        else:
            print("🔴 NEEDS IMPROVEMENT - Address critical issues")
        
        # Show key recommendations
        recommendations = qa_report.get("recommendations", [])
        if recommendations:
            print("\n🎯 Key Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec}")
        
        # Show critical issues if any
        critical_issues = qa_report.get("critical_issues", [])
        if critical_issues:
            print(f"\n🚨 Critical Issues ({len(critical_issues)}):")
            for issue in critical_issues[:3]:
                print(f"  • {issue}")
        
        print("=" * 50)
    
    def _intelligent_approval(self, phase_name: str, data: dict) -> bool:
        """Intelligent auto-approval based on quality metrics"""
        
        print(f"🤖 AI Quality Assessment: {phase_name}")
        
        # Quality checks based on phase type
        quality_score = 0
        issues = []
        
        if phase_name == "brand essence":
            # Check brand essence completeness
            required_sections = ["company_profile", "market_analysis", "brand_positioning"]
            present_sections = sum(1 for section in required_sections if data.get(section))
            quality_score = (present_sections / len(required_sections)) * 100
            
            if quality_score < 60:
                issues.append("Missing critical brand essence components")
            
        elif phase_name == "visual identity":
            # Check visual identity completeness  
            identity_data = data.get("identity", {})
            required_elements = ["palette", "typography", "logos"]
            present_elements = sum(1 for element in required_elements if identity_data.get(element))
            quality_score = (present_elements / len(required_elements)) * 100
            
            if quality_score < 60:
                issues.append("Missing critical visual identity elements")
                
        elif phase_name == "brand narrative":
            # Check narrative completeness
            required_content = ["brand_story", "voice_tone", "messaging_arch"]
            present_content = sum(1 for content in required_content if data.get(content))
            quality_score = (present_content / len(required_content)) * 100
            
            # Check content length
            total_content_length = sum(len(str(data.get(content, ""))) for content in required_content)
            if total_content_length < 300:
                quality_score *= 0.7  # Reduce score for thin content
                issues.append("Content appears too brief")
                
        elif phase_name == "brand collateral":
            # Check collateral completeness
            collateral_files = data.get("collateral_files", {})
            quality_score = min(len(collateral_files) * 20, 100)  # 20 points per file, max 100
            
            if quality_score < 60:
                issues.append("Insufficient collateral generated")
        
        else:
            quality_score = 85  # Default good score for other phases
        
        # Decision logic
        if quality_score >= 70:
            print(f"  ✅ Quality Score: {quality_score:.1f}/100 - Auto-approved")
            print("  🚀 Proceeding to next phase...")
            return True
        elif quality_score >= 50:
            print(f"  ⚠️ Quality Score: {quality_score:.1f}/100 - Acceptable, continuing with warnings")
            if issues:
                print("  📝 Issues noted:", ", ".join(issues))
            print("  🔄 Proceeding to next phase...")
            return True
        else:
            print(f"  ❌ Quality Score: {quality_score:.1f}/100 - Below acceptable threshold")
            if issues:
                print("  🚨 Critical Issues:", ", ".join(issues))
            print("  ⛔ Stopping process for quality concerns")
            return False
    
    def _save_comprehensive_outputs(self, company_name: str, brand_essence: dict, 
                                  identity_data: dict, literature_data: dict,
                                  collateral_data: dict, visual_system: dict, qa_report: dict):
        """Save all outputs in organized format with company-specific folders"""
        base_name = company_name.lower().replace(' ', '_')
        company_output_dir = os.path.join("output", base_name)
        os.makedirs(company_output_dir, exist_ok=True)
        
        # Master data file
        master_data = {
            "company_name": company_name,
            "timestamp": str(os.path.getctime(".")),
            "brand_essence": brand_essence,
            "visual_identity": identity_data,
            "brand_narrative": literature_data,
            "collateral_suite": collateral_data,
            "visual_system": visual_system,
            "qa_report": qa_report
        }
        
        master_path = os.path.join(company_output_dir, f"{base_name}_master_brandbook.json")
        with open(master_path, "w", encoding="utf-8") as f:
            json.dump(master_data, f, indent=2)
        print(f"💾 Master data saved: {master_path}")
        
        # Comprehensive markdown
        md_path = os.path.join(company_output_dir, f"{base_name}_complete_brandbook.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Complete Brand Book: {company_name}\n\n")
            f.write("## Executive Summary\n\n")
            f.write(f"**QA Score:** {qa_report.get('overall_score', 0):.1f}/100\n")
            f.write(f"**Export Formats:** {len(collateral_data.get('collateral_files', {})) + 3} files\n\n")
            f.write("## Brand Essence & Market Analysis\n\n")
            f.write(dict_to_markdown(brand_essence))
            f.write("\n\n## Visual Identity System\n\n")
            f.write(dict_to_markdown(identity_data))
            f.write("\n\n## Brand Narrative & Messaging\n\n")
            f.write(dict_to_markdown(literature_data))
            f.write("\n\n## Quality Assurance Report\n\n")
            f.write(dict_to_markdown(qa_report))
        print(f"📄 Complete markdown saved: {md_path}")
    
    def _create_professional_pptx(self, company_name: str, identity_data: dict,
                                 literature_data: dict, brand_essence: dict, visual_system: dict) -> str:
        """Create professional PowerPoint matching top agency standards"""
        print("  Creating professional-grade presentation design...")
        
        # Generate comprehensive PPTX with black background and proper text colors
        pptx_path = self.pptx_generator.create_pptx(
            company_name, identity_data, literature_data, brand_essence
        )
        
        print("  ✨ Professional presentation created with agency-level design")
        return pptx_path
    
    def _display_final_summary(self, company_name: str, export_results: dict, 
                              pptx_path: str, qa_report: dict):
        """Display final summary with all outputs"""
        print(f"\n🎉 BRAND BOOK CREATION SUMMARY")
        print("=" * 60)
        print(f"Company: {company_name}")
        print(f"Quality Score: {qa_report.get('overall_score', 0):.1f}/100")
        print(f"Total Exports: {len(export_results.get('exports', {})) + 1} formats")
        
        print(f"\n📁 OUTPUT FILES:")
        
        # Enhanced PowerPoint
        print(f"  🎯 Enhanced PowerPoint: {os.path.basename(pptx_path)}")
        
        # Advanced exports
        exports = export_results.get('exports', {})
        for format_name, file_path in exports.items():
            icon = self._get_format_icon(format_name)
            filename = os.path.basename(file_path) if isinstance(file_path, str) else f"{format_name}_package"
            print(f"  {icon} {format_name.title()}: {filename}")
        
        print(f"\n📂 All files saved in: ./output/{company_name.lower().replace(' ', '_')}/")
        
        # Final recommendations
        if qa_report.get("overall_score", 0) >= 85:
            print("🏆 Congratulations! Your brand book meets professional standards.")
        else:
            print("💡 Consider addressing QA recommendations for even better results.")
    
    def _get_format_icon(self, format_name: str) -> str:
        """Get appropriate icon for file format"""
        icons = {
            "pdf": "📄",
            "html": "🌐", 
            "print_pdf": "🖨️",
            "assets_package": "📦",
            "digital_styleguide": "💻"
        }
        return icons.get(format_name, "📄")

if __name__ == "__main__":
    orchestrator = BrandBookOrchestrator()
    orchestrator.run()