# Quick Start Guide

## For Students

### 1. Initial Setup

```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh
./setup.sh
```

### 2. Configure Your Environment

Edit `.env` file with your credentials:

```env
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
OPENAI_API_KEY=your_openai_api_key
STUDENT_SECRET=your_unique_secret
STUDENT_EMAIL=your_email@example.com
```

### 3. Start Your API Endpoint

```bash
python student_api.py
```

Your endpoint will be available at `http://localhost:5000/api/deploy`

### 4. Submit Your Endpoint

Submit your endpoint URL and secret via the instructor's Google Form.

### 5. How It Works

When you receive a task request:
- Your API automatically validates the secret
- Generates the application using LLM
- Creates a GitHub repository
- Deploys to GitHub Pages
- Notifies the evaluation system

All automatically!

## For Instructors

### 1. Setup

```bash
# Run setup script
setup.bat  # Windows
./setup.sh # Linux/Mac

# Start evaluation API
python evaluation_api.py
```

### 2. Collect Submissions

Create `submissions.csv` with:
```csv
timestamp,email,endpoint,secret
2025-10-16 10:00:00,student@example.com,https://student.com/api/deploy,secret123
```

### 3. Run Round 1

```bash
python round1.py --submissions submissions.csv
```

This will:
- Generate unique tasks for each student
- Send POST requests to their endpoints
- Track responses in the database

### 4. Evaluate Submissions

```bash
python evaluate.py
```

This will:
- Check LICENSE files
- Evaluate README quality with LLM
- Evaluate code quality with LLM
- Run Playwright tests for functional checks
- Store results in database

### 5. Run Round 2

```bash
python round2.py
```

This generates and sends Round 2 tasks based on Round 1 submissions.

## Testing Locally

### Test Student API

```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

Example `test_request.json`:
```json
{
  "email": "test@example.com",
  "secret": "your_secret",
  "task": "sum-of-sales-abc12",
  "round": 1,
  "nonce": "test-nonce-123",
  "brief": "Create a simple calculator app",
  "checks": [
    "js: document.title.includes('Calculator')",
    "js: !!document.querySelector('#result')"
  ],
  "attachments": [],
  "evaluation_url": "http://localhost:5001/api/notify"
}
```

### View Results

Query the database to see results:

```python
from models import SessionLocal, Result
db = SessionLocal()
results = db.query(Result).all()
for r in results:
    print(f"{r.email} - {r.check}: {r.score} - {r.reason}")
```

## Architecture

```
Student Side:
  Student API (student_api.py)
    ↓
  LLM Generator (llm_generator.py) → Generates HTML/CSS/JS
    ↓
  GitHub Manager (github_manager.py) → Creates repo, enables Pages
    ↓
  Notifies Evaluation API

Instructor Side:
  Round Scripts (round1.py, round2.py)
    ↓
  Task Templates (task_templates.py) → Generate unique tasks
    ↓
  POST to Student APIs
    ↓
  Evaluation API (evaluation_api.py) → Receives notifications
    ↓
  Evaluation Script (evaluate.py)
    ├── Check LICENSE
    ├── LLM README evaluation
    ├── LLM code evaluation
    └── Playwright functional tests
```

## Troubleshooting

### "Failed to create repository"
- Check your GitHub token has `repo` permissions
- Ensure the repository name doesn't already exist

### "LLM generation failed"
- Verify your OpenAI/Anthropic API key is valid
- Check API rate limits
- Ensure you have sufficient credits

### "Pages not available"
- GitHub Pages can take 2-5 minutes to deploy
- Check repository settings → Pages is enabled
- Verify the repository is public

### "Evaluation API not receiving notifications"
- Check firewall settings
- Ensure evaluation API is running
- Verify the evaluation_url is accessible

## Database Schema

### Tasks Table
- Stores sent tasks with email, task ID, round, nonce, brief, checks

### Repos Table
- Stores submitted repositories with URLs, commit SHAs

### Results Table
- Stores evaluation results with scores and reasons

## API Endpoints

### Student API
- `POST /api/deploy` - Receives task requests
- `GET /health` - Health check

### Evaluation API
- `POST /api/notify` - Receives deployment notifications
- `GET /health` - Health check

