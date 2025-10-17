import csv
import requests
import uuid
from datetime import datetime
from models import SessionLocal, Task
from task_templates import generate_task
import config
import argparse

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

def process_round1(submissions_file):
    """Process round 1 tasks for all submissions."""
    db = SessionLocal()

    try:
        # Read submissions
        with open(submissions_file, 'r') as f:
            reader = csv.DictReader(f)
            submissions = list(reader)

        print(f"Processing {len(submissions)} submissions for Round 1...\n")

        for submission in submissions:
            email = submission['email']
            endpoint = submission['endpoint']
            secret = submission['secret']

            # Check if already processed
            existing = db.query(Task).filter_by(
                email=email,
                round=1
            ).first()

            if existing and existing.statuscode == 200:
                print(f"✓ {email}: Already completed Round 1")
                continue

            print(f"Processing {email}...")

            # Generate task
            task_data = generate_task(email, round_num=1)

            # Generate nonce
            nonce = str(uuid.uuid4())

            # Build request
            request_data = {
                'email': email,
                'secret': secret,
                'task': task_data['task_id'],
                'round': 1,
                'nonce': nonce,
                'brief': task_data['brief'],
                'checks': task_data['checks'],
                'attachments': task_data['attachments'],
                'evaluation_url': f"{config.EVALUATION_API_BASE_URL}/api/notify"
            }

            # Send request
            print(f"  Sending task: {task_data['task_id']}")
            status_code = send_task_request(endpoint, request_data)

            # Log to database
            task = Task(
                timestamp=datetime.utcnow(),
                email=email,
                task=task_data['task_id'],
                round=1,
                nonce=nonce,
                brief=task_data['brief'],
                attachments=str(task_data['attachments']),
                checks=str(task_data['checks']),
                evaluation_url=f"{config.EVALUATION_API_BASE_URL}/api/notify",
                endpoint=endpoint,
                statuscode=status_code,
                secret=secret
            )
            db.add(task)
            db.commit()

            if status_code == 200:
                print(f"  ✓ Success (HTTP {status_code})")
            else:
                print(f"  ✗ Failed (HTTP {status_code})")

            print()

        print("Round 1 processing complete!")

    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Round 1 tasks')
    parser.add_argument('--submissions', required=True, help='Path to submissions.csv')
    args = parser.parse_args()

    process_round1(args.submissions)

