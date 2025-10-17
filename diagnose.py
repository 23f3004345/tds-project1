import sys
import traceback

def diagnose_startup():
    """Diagnose why the Flask app won't start"""
    print("=== Flask Startup Diagnosis ===")

    try:
        print("1. Testing Flask import...")
        import flask
        print(f"   ✓ Flask {flask.__version__} imported successfully")

        print("2. Testing config import...")
        import config
        print(f"   ✓ Config imported - LLM Provider: {config.LLM_PROVIDER}")
        print(f"   ✓ API Port: {config.API_PORT}")

        print("3. Testing other imports...")
        from llm_generator import LLMGenerator
        print("   ✓ LLMGenerator imported")

        from github_manager import GitHubManager
        print("   ✓ GitHubManager imported")

        print("4. Testing Flask app creation...")
        from student_api import app
        print("   ✓ Flask app imported successfully")

        print("5. Starting Flask server...")
        print(f"   🚀 Server starting on http://127.0.0.1:{config.API_PORT}")
        print("   Available at: http://127.0.0.1:5000")
        print("   Press Ctrl+C to stop")
        print("=" * 40)

        # Start the server
        app.run(host='127.0.0.1', port=config.API_PORT, debug=True, use_reloader=False)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        print("\n" + "="*50)
        print("SOLUTION:")
        if "ModuleNotFoundError" in str(e):
            print("- Install missing dependencies: pip install -r requirements.txt")
        elif "port" in str(e).lower() or "address" in str(e).lower():
            print("- Port 5000 might be in use. Try a different port.")
        else:
            print("- Check the error message above and fix the configuration issue")
        print("="*50)

        input("\nPress Enter to exit...")

if __name__ == "__main__":
    diagnose_startup()
