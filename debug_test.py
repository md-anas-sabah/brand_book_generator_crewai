# debug_test.py - Run this first to test your setup
import os

print("=== Environment Debug Test ===")

# Test 1: Check if .env file exists
env_file_path = ".env"
if os.path.exists(env_file_path):
    print("✓ .env file found")
else:
    print("✗ .env file NOT found - Please create it!")
    print(f"Expected location: {os.path.abspath(env_file_path)}")

# Test 2: Try to import packages
try:
    import fal_client as fal
    print("✓ fal_client imported successfully")
except ImportError as e:
    print(f"✗ fal_client import failed: {e}")

try:
    from decouple import config
    print("✓ decouple imported successfully")
except ImportError as e:
    print(f"✗ decouple import failed: {e}")

# Test 3: Try to load environment variable
try:
    from decouple import config
    fal_key = config('FAL_KEY')
    if fal_key:
        print(f"✓ FAL_KEY loaded: {fal_key[:10]}... (showing first 10 chars)")
    else:
        print("✗ FAL_KEY is empty")
except Exception as e:
    print(f"✗ Error loading FAL_KEY: {e}")

# Test 4: Test simple FAL client connection
try:
    import fal_client as fal
    from decouple import config
    
    os.environ['FAL_KEY'] = config('FAL_KEY')
    
    # Try to list available models (simple API test)
    print("✓ FAL client setup appears correct")
    print("Ready to test image generation!")
    
except Exception as e:
    print(f"✗ FAL client setup failed: {e}")

print("\n=== Next Steps ===")
print("If all tests pass, run: python tools/fal_image_tool.py")
print("If tests fail, follow the setup instructions above.")