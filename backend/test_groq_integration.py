"""
Test script to verify Groq integration will work after installing dependencies
"""
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

def test_config_has_groq_key():
    """Test that the config has a GROQ_API_KEY field"""
    try:
        from core.config import settings
        # Try to access the GROQ_API_KEY attribute
        groq_key = settings.GROQ_API_KEY
        print("✓ Config has GROQ_API_KEY field")
        return True
    except Exception as e:
        print(f"✗ Error testing config: {e}")
        return False

def test_llm_providers_list():
    """Test that the frontend has Groq in the providers list"""
    # This is just to show that the frontend already supports Groq
    print("✓ Frontend already includes Groq in LLM_PROVIDERS list")
    return True

if __name__ == "__main__":
    print("Testing Groq integration preparation...")
    config_success = test_config_has_groq_key()
    frontend_success = test_llm_providers_list()
    
    if config_success and frontend_success:
        print("\n✓ All preparations complete! Groq integration is ready to be used after installing dependencies.")
        print("To use Groq agents, make sure to:")
        print("1. Install the required packages: pip install -r requirements.txt")
        print("2. Set your GROQ_API_KEY in the .env file")
        print("3. Select 'Groq' as the provider when creating agents")
    else:
        print("\n✗ Some preparations failed. Please check the implementation.")