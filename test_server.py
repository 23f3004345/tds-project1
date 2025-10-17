import os
import sys
from flask import Flask, jsonify

# Simple test server to verify Flask is working
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'status': 'Server is running!',
        'message': 'Flask application is working correctly',
        'endpoints': {
            '/': 'This page',
            '/health': 'Health check',
            '/api/deploy': 'Main deployment endpoint'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'student-api'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Flask Test Server")
    print("=" * 50)
    print("Server will be available at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)

    try:
        app.run(host='127.0.0.1', port=5000, debug=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        input("Press Enter to exit...")
