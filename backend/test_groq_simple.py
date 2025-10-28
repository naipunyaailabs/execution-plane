"""
Simple test to verify Groq integration
"""
def test_groq_import():
    try:
        from langchain_groq import ChatGroq
        print("✓ Successfully imported ChatGroq")
        return True
    except ImportError as e:
        print(f"✗ Failed to import ChatGroq: {e}")
        return False

def test_settings_import():
    try:
        from core.config import settings
        # Check if GROQ_API_KEY attribute exists
        if hasattr(settings, 'GROQ_API_KEY'):
            print("✓ Settings has GROQ_API_KEY attribute")
            return True
        else:
            print("✗ Settings missing GROQ_API_KEY attribute")
            return False
    except Exception as e:
        print(f"✗ Error importing settings: {e}")
        return False

if __name__ == "__main__":
    print("Testing Groq integration...")
    groq_import = test_groq_import()
    settings_test = test_settings_import()
    
    if groq_import and settings_test:
        print("\n✓ Groq integration is ready!")
    else:
        print("\n✗ Groq integration has issues.")