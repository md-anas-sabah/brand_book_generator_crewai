"""
Live PPTX Development - Edit Python, See Changes in Browser
Real web dev workflow for PowerPoint generation
"""

import os
import time
import subprocess
import webbrowser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tools.enhanced_pptx_generator import EnhancedPPTXGenerator

class LivePPTXHandler(FileSystemEventHandler):
    """Watches for changes in PPTX generator and auto-regenerates"""
    
    def __init__(self):
        self.generator = EnhancedPPTXGenerator()
        self.last_generated = 0
        
        # Test data for live development
        self.test_data = {
            "company_name": "TechForward Live",
            "identity_data": {
                "logos": [
                    "/Users/anassabah/Downloads/Marqait/brand book_crew/output/zeta_logo_1_20250828_235333_3e1fde11.png",
                    "/Users/anassabah/Downloads/Marqait/brand book_crew/output/zeta_logo_2_20250828_235352_a3259202.png",
                    "/Users/anassabah/Downloads/Marqait/brand book_crew/output/zeta_logo_3_20250828_235415_054bae29.png"
                ],
                "palette": {"primary": "#2E86AB", "secondary": "#A23B72", "accent": "#F18F01"},
                "typography": {"primary": "Inter", "secondary": "Source Sans Pro"},
                "visual_style": "Modern, clean, professional, minimalist, bold typography",
                "photography_style": "High contrast, authentic moments, natural lighting"
            },
            "literature_data": {
                "brand_story": "We revolutionize technology through innovative design and human-centered solutions that empower businesses to achieve their digital transformation goals.",
                "voice_tone": "Professional yet approachable, confident, innovative, and human-centered with a focus on clarity and trust.",
                "messaging_arch": "Our core message centers on bridging the gap between complex technology and intuitive user experiences.",
                "marketing_copy": {
                    "website": "Transform your digital experience with our cutting-edge solutions designed for the modern business landscape.",
                    "social_media": "Innovation meets simplicity. Technology that works for you. #TechForHumans #DigitalTransformation"
                },
                "collaterals": {
                    "business_card": "Clean, modern design with QR code integration and minimal brand elements",
                    "letterhead": "Professional header with subtle brand accents and contact information"
                }
            },
            "brand_essence": {
                "company_profile": {
                    "name": "TechForward Inc",
                    "industry": "Technology & Digital Solutions",
                    "target_audience": "Progressive businesses seeking digital transformation and innovation",
                    "core_values": ["Innovation", "Simplicity", "Human-Centered", "Excellence", "Trust", "Reliability"]
                },
                "brand_positioning": {
                    "unique_value_proposition": "We bridge the gap between complex technology and intuitive user experiences through human-centered design",
                    "brand_promise": "Technology that enhances human potential without adding complexity to your workflow",
                    "brand_personality": ["Innovative", "Reliable", "Approachable", "Progressive", "Trustworthy"],
                    "competitive_advantage": "Our deep understanding of human psychology and behavior drives more intuitive and effective technology solutions"
                },
                "market_analysis": {
                    "industry_trends": [
                        "AI-driven automation solutions",
                        "Human-centered design principles",
                        "Low-code/no-code platforms",
                        "Remote collaboration tools",
                        "Sustainable technology practices"
                    ],
                    "competitor_insights": {
                        "notable_competitors": ["Microsoft", "Google Workspace", "Salesforce", "Adobe", "Figma", "Notion"]
                    },
                    "design_trends": {
                        "design_styles": ["Minimalist interfaces", "Bold typography", "Gradient backgrounds", "Micro-interactions"]
                    }
                }
            }
        }
    
    def on_modified(self, event):
        if event.src_path.endswith('.py') and 'enhanced_pptx_generator' in event.src_path:
            current_time = time.time()
            
            # Avoid spam regeneration
            if current_time - self.last_generated < 2:
                return
                
            self.last_generated = current_time
            print(f"\n🔄 Detected changes in: {event.src_path}")
            self.regenerate_and_open()
    
    def regenerate_and_open(self):
        """Regenerate PPTX and open in browser/viewer"""
        try:
            print("🎨 Regenerating PPTX with latest changes...")
            
            # Close any existing PowerPoint files first
            try:
                subprocess.run(['pkill', '-f', 'Microsoft PowerPoint'], check=False)
                time.sleep(0.5)  # Brief pause to let PowerPoint close
            except:
                pass
            
            # Reload the module to get latest changes
            import importlib
            import tools.enhanced_pptx_generator
            importlib.reload(tools.enhanced_pptx_generator)
            
            # Create fresh instance
            from tools.enhanced_pptx_generator import EnhancedPPTXGenerator
            generator = EnhancedPPTXGenerator()
            
            # Generate with test data
            pptx_path = generator.create_pptx(
                self.test_data["company_name"],
                self.test_data["identity_data"], 
                self.test_data["literature_data"],
                self.test_data["brand_essence"]
            )
            
            print(f"✅ Generated: {pptx_path}")
            
            # Wait a moment for file to be completely written
            time.sleep(1)
            
            # Auto-open in default application
            self.open_file(pptx_path)
            
        except Exception as e:
            print(f"❌ Error regenerating: {e}")
    
    def open_file(self, file_path):
        """Open file in default application"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.run(['open', file_path], check=True)  # macOS
                # subprocess.run(['xdg-open', file_path])  # Linux
            
            print(f"📱 Opened: {file_path}")
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Could not auto-open file: {e}")
            print(f"📁 Manually open: {file_path}")
            # Try to reveal in Finder instead
            try:
                subprocess.run(['open', '-R', file_path], check=True)
                print(f"📂 Revealed in Finder: {file_path}")
            except:
                pass
        except Exception as e:
            print(f"⚠️ Could not auto-open file: {e}")
            print(f"📁 Manually open: {file_path}")

def start_live_development():
    """Start live development mode"""
    print("🚀 LIVE PPTX DEVELOPMENT MODE")
    print("=" * 50)
    print("📝 Edit: tools/enhanced_pptx_generator.py")
    print("👀 Watch: Auto-regeneration on file save")
    print("📱 Open: PPTX opens automatically")
    print("🔄 Workflow: Edit → Save → See Changes")
    print("⏹️  Stop: Press Ctrl+C")
    print("=" * 50)
    
    # Generate initial version
    handler = LivePPTXHandler()
    print("\n🎨 Generating initial version...")
    handler.regenerate_and_open()
    
    # Watch for file changes
    observer = Observer()
    observer.schedule(handler, path='tools/', recursive=True)
    observer.start()
    
    try:
        print("\n👀 Watching for changes... (Press Ctrl+C to stop)")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n⏹️ Stopped live development mode")
    
    observer.join()

def quick_test():
    """Quick test with different brand data"""
    print("🧪 QUICK TEST - Different Brand Colors")
    
    test_variations = [
        {"primary": "#E74C3C", "name": "Red Theme"},
        {"primary": "#27AE60", "name": "Green Theme"}, 
        {"primary": "#9B59B6", "name": "Purple Theme"},
        {"primary": "#F39C12", "name": "Orange Theme"}
    ]
    
    handler = LivePPTXHandler()
    
    for i, variation in enumerate(test_variations):
        print(f"\n🎨 Generating {variation['name']}...")
        
        # Update test data
        handler.test_data["identity_data"]["palette"]["primary"] = variation["primary"]
        handler.test_data["company_name"] = f"TestCorp {variation['name']}"
        
        # Generate
        handler.regenerate_and_open()
        
        if i < len(test_variations) - 1:
            input("⏸️ Press Enter for next variation...")

if __name__ == "__main__":
    print("🎯 Choose mode:")
    print("1. Live Development (watches file changes)")
    print("2. Quick Test (different color themes)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        # Install watchdog if not present
        try:
            import watchdog
        except ImportError:
            print("📦 Installing watchdog...")
            subprocess.run(["pip", "install", "watchdog"])
            import watchdog
        
        start_live_development()
    elif choice == "2":
        quick_test()
    else:
        print("🎨 Running single generation...")
        handler = LivePPTXHandler()
        handler.regenerate_and_open()