#!/usr/bin/env python3
"""
Simple script to start the Flask server with proper error handling
"""
import sys
import os

def main():
    try:
        print("Starting Flask server...")
        print("Current directory:", os.getcwd())

        # Test imports first
        print("Testing imports...")
        import config
        print(f"✓ Config loaded - LLM Provider: {config.LLM_PROVIDER}")
        print(f"✓ API Port: {config.API_PORT}")

        from llm_generator import LLMGenerator
        print("✓ LLMGenerator imported")

        from github_manager import GitHubManager
        print("✓ GitHubManager imported")

        # Import Flask app
        from student_api import app
        print("✓ Flask app imported")

        # Start the server
        print(f"\n🚀 Starting server on http://127.0.0.1:{config.API_PORT}")
        print("Available endpoints:")
        print("  - GET  /health - Health check")
        print("  - POST /api/deploy - Deploy application")
        print("\nPress Ctrl+C to stop the server")

        app.run(
            host='127.0.0.1',
            port=config.API_PORT,
            debug=True,
            use_reloader=False
        )

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
