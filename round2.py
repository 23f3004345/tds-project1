                print(f"  ✗ Failed (HTTP {status_code})")

            print()

        print("Round 2 processing complete!")

    finally:
        db.close()

if __name__ == "__main__":
    process_round2()
import uuid
from datetime import datetime
from models import SessionLocal, Task, Repo
from task_templates import generate_task
import config
import requests

def send_task_request(endpoint, task_data):
    """Send task request to student endpoint."""
    try:
        response = requests.post(
            endpoint,
            json=task_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        return response.status_code
    except Exception as e:
        print(f"Error sending request: {e}")
        return None

def process_round2():
    """Process round 2 tasks for all successful round 1 submissions."""
    db = SessionLocal()

    try:
        # Get all round 1 repos
        round1_repos = db.query(Repo).filter_by(round=1).all()

        print(f"Processing {len(round1_repos)} submissions for Round 2...\n")

        for repo in round1_repos:
            email = repo.email
            task_id = repo.task

            # Check if already processed round 2
            existing = db.query(Task).filter_by(
                email=email,
                task=task_id,
                round=2
            ).first()

            if existing and existing.statuscode == 200:
                print(f"✓ {email}: Already completed Round 2")
                continue

            # Get original task to find endpoint and secret
            original_task = db.query(Task).filter_by(
                email=email,
                task=task_id,
                round=1
            ).first()

            if not original_task:
                print(f"✗ {email}: No original task found")
                continue

            print(f"Processing {email} - {task_id}...")

            # Extract template ID from task_id (format: template-hash)
            template_id = task_id.rsplit('-', 1)[0]

            # Generate round 2 task
            task_data = generate_task(email, template_id=template_id, round_num=2, existing_task_id=task_id)

            # Generate new nonce
            nonce = str(uuid.uuid4())

            # Build request
            request_data = {
                'email': email,
                'secret': original_task.secret,
                'task': task_id,  # Keep same task ID
                'round': 2,
                'nonce': nonce,
                'brief': task_data['brief'],
                'checks': task_data['checks'],
                'attachments': task_data['attachments'],
                'evaluation_url': f"{config.EVALUATION_API_BASE_URL}/api/notify"
            }

            # Send request
            print(f"  Sending round 2 task...")
            status_code = send_task_request(original_task.endpoint, request_data)

            # Log to database
            task = Task(
                timestamp=datetime.utcnow(),
                email=email,
                task=task_id,
                round=2,
                nonce=nonce,
                brief=task_data['brief'],
                attachments=str(task_data['attachments']),
                checks=str(task_data['checks']),
                evaluation_url=f"{config.EVALUATION_API_BASE_URL}/api/notify",
                endpoint=original_task.endpoint,
                statuscode=status_code,
                secret=original_task.secret
            )
            db.add(task)
            db.commit()

            if status_code == 200:
                print(f"  ✓ Success (HTTP {status_code})")
            else:

