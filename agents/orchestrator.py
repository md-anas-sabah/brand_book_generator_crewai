from agents.identity_agent import IdentityAgent
from agents.literature_agent import LiteratureAgent
from tools.pptx_generator import PPTXGenerator
import os
import markdown2

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
    def __init__(self):
        self.identity_agent = IdentityAgent()
        self.literature_agent = LiteratureAgent()
        self.pptx_generator = PPTXGenerator()
    
    def run(self):
        print("=== Brand Book Creator ===")
        company_name = input("Company name: ").strip()
        industry = input("Industry: ").strip()
        values = input("Company values (comma-separated): ").strip()
        audience = input("Target audience: ").strip()
        logo_style = input("Logo/brand style (minimalistic, colourful, random, etc): ").strip()

        print("\n[1/3] Creating brand identity assets...\n")
        identity_data = self.identity_agent.create_identity(
            company_name, industry, values, audience, logo_style
        )
        print("\n[IDENTITY AGENT OUTPUT]\n")
        identity_md = dict_to_markdown(identity_data, "Brand Identity Output")
        print(identity_md)

        print("\n[2/3] Creating brand literature & collateral...\n")
        literature_data = self.literature_agent.create_literature(
            company_name, industry, values, audience
        )
        print("\n[LITERATURE AGENT OUTPUT]\n")
        literature_md = dict_to_markdown(literature_data, "Brand Literature Output")
        print(literature_md)

        # Save all output as markdown
        os.makedirs("output", exist_ok=True)
        md_path = os.path.join(
            "output", f"{company_name.lower().replace(' ', '_')}_brandbook_output.md"
        )
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Brand Book Raw Output: {company_name}\n\n")
            f.write(identity_md)
            f.write("\n\n---\n\n")
            f.write(literature_md)
        print(f"\n🔖 Agent output saved as Markdown: {md_path}")

        # (Optional) Save as HTML using markdown2 for a pretty preview
        html_path = md_path.replace(".md", ".html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(markdown2.markdown_path(md_path))
        print(f"🔖 Pretty HTML preview saved: {html_path}")

        print("\n[3/3] Generating PowerPoint Brand Book...\n")
        pptx_path = self.pptx_generator.create_pptx(
            company_name, identity_data, literature_data
        )
        print(f"\n✅ Done! Brand Book PPTX created at: {pptx_path}\n")

if __name__ == "__main__":
    orchestrator = BrandBookOrchestrator()
    orchestrator.run()
