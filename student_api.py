from flask import Flask, request, jsonify
import config
from llm_generator import LLMGenerator
from github_manager import GitHubManager
import requests
import time
import json

app = Flask(__name__)

def verify_secret(secret):
    """Verify the secret matches the student's secret."""
    return secret == config.STUDENT_SECRET

def send_to_evaluation(data, evaluation_url, max_retries=5):
    """Send deployment info to evaluation URL with exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                evaluation_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            if response.status_code == 200:
                print(f"Successfully notified evaluation API: {response.text}")
                return True
            else:
                print(f"Evaluation API returned {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Error sending to evaluation API (attempt {attempt + 1}): {e}")

        if attempt < max_retries - 1:
            delay = config.RETRY_DELAYS[attempt] if attempt < len(config.RETRY_DELAYS) else 16
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)

    return False

@app.route('/api/deploy', methods=['POST'])
def deploy():
    """Main endpoint to receive task requests and deploy apps."""
    try:
        # Parse request
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'secret', 'task', 'round', 'nonce', 'brief', 'checks', 'evaluation_url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Verify secret
        if not verify_secret(data['secret']):
            return jsonify({'error': 'Invalid secret'}), 401

        print(f"\n{'='*60}")
        print(f"Received task request: {data['task']} (Round {data['round']})")
        print(f"Email: {data['email']}")
        print(f"Brief: {data['brief'][:100]}...")
        print(f"{'='*60}\n")

        # Extract data
        task_id = data['task']
        round_num = data['round']
        brief = data['brief']
        checks = data['checks']
        attachments = data.get('attachments', [])
        evaluation_url = data['evaluation_url']
        nonce = data['nonce']
        email = data['email']

        # Initialize generators
        llm_gen = LLMGenerator()
        gh_manager = GitHubManager()

        # Generate or update app
        if round_num == 1:
            print("Generating new application...")

            # Generate HTML
            html_content = llm_gen.generate_app(brief, checks, attachments)
            print(f"Generated HTML ({len(html_content)} characters)")

            # Generate README
            readme_content = llm_gen.generate_readme(brief, task_id, f"task-{task_id}")
            print(f"Generated README ({len(readme_content)} characters)")

            # Deploy to GitHub
            print("Deploying to GitHub...")
            deployment = gh_manager.deploy_app(task_id, html_content, readme_content, attachments)

        else:  # Round 2+
            print(f"Updating existing application (Round {round_num})...")

            # Generate updated HTML
            html_content = llm_gen.generate_app(brief, checks, attachments)
            print(f"Generated updated HTML ({len(html_content)} characters)")

            # Generate updated README
            repo_name = f"task-{task_id}"
            readme_content = llm_gen.generate_readme(brief, task_id, repo_name)
            print(f"Generated updated README ({len(readme_content)} characters)")

            # Update GitHub repo
            print("Updating GitHub repository...")
            deployment = gh_manager.update_app(repo_name, html_content, readme_content)

        print(f"\nDeployment complete!")
        print(f"Repo: {deployment['repo_url']}")
        print(f"Commit: {deployment['commit_sha']}")
        print(f"Pages: {deployment['pages_url']}")

        # Prepare evaluation notification
        eval_data = {
            'email': email,
            'task': task_id,
            'round': round_num,
            'nonce': nonce,
            'repo_url': deployment['repo_url'],
            'commit_sha': deployment['commit_sha'],
            'pages_url': deployment['pages_url']
        }

        # Send to evaluation API
        print(f"\nNotifying evaluation API: {evaluation_url}")
        success = send_to_evaluation(eval_data, evaluation_url)

        if success:
            print("Evaluation API notified successfully!")
        else:
            print("Warning: Failed to notify evaluation API after all retries")

        # Return success response
        return jsonify({
            'status': 'success',
            'message': 'Application deployed successfully',
            'repo_url': deployment['repo_url'],
            'commit_sha': deployment['commit_sha'],
            'pages_url': deployment['pages_url'],
            'evaluation_notified': success
        }), 200

    except Exception as e:
        print(f"Error processing request: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'student-api'}), 200

@app.route('/', methods=['GET'])
def home():
    """Root endpoint with API information."""
    return jsonify({
        'service': 'Student API - LLM Code Deployment System',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'This information page',
            'GET /health': 'Health check endpoint',
            'POST /api/deploy': 'Main deployment endpoint for task requests'
        },
        'usage': {
            'deploy': {
                'method': 'POST',
                'url': '/api/deploy',
                'required_fields': ['email', 'secret', 'task', 'round', 'nonce', 'brief', 'checks', 'evaluation_url'],
                'description': 'Submit a task for LLM-generated application deployment'
            }
        },
        'configuration': {
            'llm_provider': config.LLM_PROVIDER,
            'github_username': config.GITHUB_USERNAME,
            'api_port': config.API_PORT
        }
    }), 200

if __name__ == '__main__':
    print(f"Starting Student API on port {config.API_PORT}...")
    print(f"GitHub Username: {config.GITHUB_USERNAME}")
    print(f"LLM Provider: {config.LLM_PROVIDER}")
    app.run(host='0.0.0.0', port=config.API_PORT, debug=False)
