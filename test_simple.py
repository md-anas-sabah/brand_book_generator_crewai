#!/usr/bin/env python3

# Simple test script to check basic functionality
import sys
import os

print("🧪 Testing Brand Book Generator Components...")

try:
    # Test basic imports
    print("📦 Testing basic imports...")
    from agents.brand_strategist_agent import BrandStrategistAgent
    print("  ✅ BrandStrategistAgent imported successfully")
    
    from agents.identity_agent import IdentityAgent
    print("  ✅ IdentityAgent imported successfully")
    
    from agents.literature_agent import LiteratureAgent
    print("  ✅ LiteratureAgent imported successfully")
    
    print("📦 Testing advanced imports...")
    from agents.collateral_agent import CollateralAgent
    print("  ✅ CollateralAgent imported successfully")
    
    from agents.qa_compliance_agent import QAComplianceAgent
    print("  ✅ QAComplianceAgent imported successfully")
    
    from tools.pptx_generator import PPTXGenerator
    print("  ✅ PPTXGenerator imported successfully")
    
    print("📦 Testing orchestrator...")
    from agents.orchestrator import BrandBookOrchestrator
    print("  ✅ BrandBookOrchestrator imported successfully")
    
    print("\n🎉 All core components loaded successfully!")
    print("🚀 Ready to create world-class brand books!")
    
    # Quick functionality test
    print("\n🔬 Running quick functionality test...")
    
    # Test basic agent creation (without API calls)
    identity_agent = IdentityAgent()
    literature_agent = LiteratureAgent()
    qa_agent = QAComplianceAgent()
    
    print("  ✅ Agents initialized successfully")
    print("  ✅ System is ready for brand book creation!")
    
    print("\n" + "="*60)
    print("🏆 BRAND BOOK GENERATOR - READY FOR USE")
    print("="*60)
    print("Run: python3 main.py")
    print("To create your first world-class brand book!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Try installing missing dependencies:")
    print("   pip3 install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)