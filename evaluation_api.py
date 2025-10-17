from flask import Flask, request, jsonify
from models import SessionLocal, Task, Repo
from datetime import datetime

app = Flask(__name__)

@app.route('/api/notify', methods=['POST'])
def notify():
    """Receive deployment notifications from students."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'task', 'round', 'nonce', 'repo_url', 'commit_sha', 'pages_url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        db = SessionLocal()

        try:
            # Check if task exists with matching email, task, round, nonce
            task = db.query(Task).filter_by(
                email=data['email'],
                task=data['task'],
                round=data['round'],
                nonce=data['nonce']
            ).first()

            if not task:
                return jsonify({'error': 'Invalid task, round, or nonce'}), 400

            # Check if already submitted
            existing = db.query(Repo).filter_by(
                email=data['email'],
                task=data['task'],
                round=data['round'],
                nonce=data['nonce']
            ).first()

            if existing:
                return jsonify({'message': 'Already submitted', 'status': 'duplicate'}), 200

            # Create repo entry
            repo = Repo(
                timestamp=datetime.utcnow(),
                email=data['email'],
                task=data['task'],
                round=data['round'],
                nonce=data['nonce'],
                repo_url=data['repo_url'],
                commit_sha=data['commit_sha'],
                pages_url=data['pages_url']
            )

            db.add(repo)
            db.commit()

            print(f"Received submission: {data['email']} - {data['task']} (Round {data['round']})")
            print(f"  Repo: {data['repo_url']}")
            print(f"  Pages: {data['pages_url']}")

            return jsonify({
                'status': 'success',
                'message': 'Submission received and queued for evaluation'
            }), 200

        finally:
            db.close()

    except Exception as e:
        print(f"Error processing notification: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'evaluation-api'}), 200

if __name__ == '__main__':
    print("Starting Evaluation API on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=False)

