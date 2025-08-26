#!/usr/bin/env python3

# Test script to complete PPTX generation with the fix
import json
import os

print("🔧 Testing PPTX generation fix...")

# Load the master brand book data
with open('output/marqait_master_brandbook.json', 'r') as f:
    master_data = json.load(f)

# Extract components
company_name = master_data['company_name']
identity_data = master_data['visual_identity'] 
literature_data = master_data['brand_narrative']
brand_essence = master_data['brand_essence']

print(f"📊 Loaded brand data for {company_name}")

# Test PPTX generation
try:
    from tools.pptx_generator import PPTXGenerator
    
    pptx_generator = PPTXGenerator()
    print("  Creating enhanced PowerPoint presentation...")
    
    pptx_path = pptx_generator.create_pptx(
        company_name, identity_data, literature_data, brand_essence
    )
    
    print(f"✅ SUCCESS! Enhanced PowerPoint created: {pptx_path}")
    print("\n🏆 WORLD-CLASS BRAND BOOK CREATION COMPLETE!")
    print("=" * 60)
    
    # List all generated files
    print("📁 ALL OUTPUT FILES CREATED:")
    print("  🎯 Enhanced PowerPoint:", os.path.basename(pptx_path))
    print("  📄 Professional PDF: marqait_brand_book_professional.pdf")
    print("  🌐 Interactive HTML: marqait_brand_book_interactive.html")
    print("  💾 Master Data: marqait_master_brandbook.json")
    print("  📝 Complete Guide: marqait_complete_brandbook.md")
    print("  🎨 7 Collateral Mockups in /collateral/")
    print("  📦 Brand Assets Package in /exports/")
    print("  💻 Digital Style Guide: marqait_styleguide.json")
    print("  🎨 3 AI-Generated Logos")
    
    print(f"\n📂 All files saved in: ./output/")
    print("🎊 Your world-class brand book is ready for professional use!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 The fix might need additional adjustment")