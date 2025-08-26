import os
from tools.branding_resources import (
    get_brand_story_prompt,
    get_voice_tone_prompt,
    get_messaging_prompt,
    get_marketing_copy_prompts,
    get_collateral_templates,
)
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_openai(prompt, max_tokens=300, temperature=0.7):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


class LiteratureAgent:
    """
    Generates brand literature and copy:
    - Brand story/mission
    - Brand voice and tone
    - Messaging & key values
    - Marketing copy templates
    - Collateral (business card, email signature, etc.)
    """
    def create_literature(self, company_name, industry, values, audience):
        # 1. Brand Story & Mission
        print(f"Generating brand story and mission for {company_name}...")
        brand_story_prompt = get_brand_story_prompt(company_name, industry, values, audience)
        brand_story = call_openai(brand_story_prompt)
        
        # 2. Voice and Tone
        print(f"Generating brand voice and tone guidelines for {company_name}...")
        voice_tone_prompt = get_voice_tone_prompt(company_name, industry, values, audience)
        voice_tone = call_openai(voice_tone_prompt, max_tokens=120)
        
        # 3. Messaging Architecture & Key Value Propositions
        print(f"Generating messaging architecture for {company_name}...")
        messaging_prompt = get_messaging_prompt(company_name, industry, values, audience)
        messaging_arch = call_openai(messaging_prompt, max_tokens=180)
        
        # 4. Marketing Copy Templates
        print(f"Generating marketing copy templates for {company_name}...")
        marketing_prompts = get_marketing_copy_prompts(company_name, industry, values, audience)
        marketing_copy = {}
        for channel, prompt in marketing_prompts.items():
            marketing_copy[channel] = call_openai(prompt, max_tokens=120)
        
        # 5. Collateral Templates (Descriptions Only)
        print(f"Generating collateral templates for {company_name}...")
        collateral_templates = get_collateral_templates(company_name, industry, values, audience)
        
        return {
            "brand_story": brand_story,
            "voice_tone": voice_tone,
            "messaging_arch": messaging_arch,
            "marketing_copy": marketing_copy,
            "collaterals": collateral_templates,
        }

# Example test usage
if __name__ == "__main__":
    agent = LiteratureAgent()
    output = agent.create_literature(
        company_name="Acme Corp",
        industry="Fintech",
        values="Trust, Innovation, Simplicity",
        audience="Young professionals"
    )
    from pprint import pprint
    pprint(output)
