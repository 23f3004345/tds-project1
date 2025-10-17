setup.batsetup.bat# FAQ - Frequently Asked Questions

## General Questions

### Q: What does this system do?
A: This system automates the process of building, deploying, and evaluating student web applications. Students receive task requests, their system uses LLMs to generate code, deploys to GitHub Pages, and gets automatically evaluated.

### Q: Why use LLMs for code generation?
A: LLMs can quickly generate production-ready code based on natural language briefs, allowing students to focus on the deployment and evaluation pipeline rather than writing code from scratch.

### Q: What programming languages are used?
A: Python for the backend/automation, and HTML/CSS/JavaScript for the generated applications.

## Setup Questions

### Q: Do I need a paid OpenAI account?
A: Yes, you'll need API credits. Alternatively, you can use Anthropic's Claude or any other LLM provider by modifying `llm_generator.py`.

### Q: What GitHub permissions do I need?
A: Your personal access token needs: `repo`, `delete_repo`, `admin:repo_hook`, and `workflow` permissions.

### Q: Can I use a different database than SQLite?
A: Yes! For production, PostgreSQL is recommended. Just change `DATABASE_URL` in your `.env` file.

### Q: How much does this cost to run?
A: Main costs are:
- OpenAI API: ~$0.01-0.10 per task (depending on model)
- GitHub: Free (public repos)
- Hosting: Free tier available on Railway/Render

## Student Questions

### Q: What if my API endpoint goes down?
A: Instructors can retry sending tasks. Make sure your endpoint has good uptime.

### Q: Can I test without deploying?
A: Yes! Use `test_api.py` to test locally before submitting your endpoint.

### Q: What if the generated code doesn't pass checks?
A: The LLM generator is designed to follow the brief and checks. If it fails, you may need to fine-tune the prompts in `llm_generator.py`.

### Q: How long does deployment take?
A: Typically 30-60 seconds for code generation + 2-5 minutes for GitHub Pages to go live.

### Q: Can I modify the generated code?
A: Not for this project - the point is to build an automated system. However, you can improve your LLM prompts.

## Instructor Questions

### Q: How do I create custom tasks?
A: Edit `task_templates.py` and add new templates following the existing format.

### Q: Can I run multiple rounds?
A: Yes! The system supports unlimited rounds. Round 1 creates new apps, subsequent rounds modify them.

### Q: How are scores calculated?
A: Each check gets a score (0-1), and the overall score is the average. LLM evaluations return scores 0-10 which are normalized.

### Q: What if a student's repo is private?
A: The evaluation will fail. Students must make repos public as per requirements.

### Q: Can I export results?
A: Yes! Query the `results` table and export to CSV:
```python
from models import SessionLocal, Result
import pandas as pd

db = SessionLocal()
results = pd.read_sql(db.query(Result).statement, db.bind)
results.to_csv('results.csv', index=False)
```

## Technical Questions

### Q: Why does Playwright need chromium?
A: Playwright runs functional tests by actually loading the deployed pages in a browser and executing JavaScript checks.

### Q: Can I use a different LLM provider?
A: Yes! The system supports OpenAI and Anthropic out of the box. For others, modify `llm_generator.py`.

### Q: How are secrets verified?
A: Each student provides a secret in the form. Incoming requests must include this secret, which is checked before processing.

### Q: What happens if GitHub Pages deployment fails?
A: The system will still return the repo URL and commit SHA, but Pages URL might not be accessible. The evaluation will fail on dynamic checks.

### Q: Can I run this on Windows?
A: Yes! All scripts work on Windows, Linux, and Mac. Use `setup.bat` for Windows setup.

## Troubleshooting

### Q: "ModuleNotFoundError: No module named 'flask'"
A: Run the setup script or manually: `pip install -r requirements.txt`

### Q: "GitHub API rate limit exceeded"
A: You're making too many API calls. Wait an hour or use multiple tokens.

### Q: "Playwright browser not found"
A: Run: `playwright install chromium`

### Q: Generated code doesn't work
A: Check the LLM prompts in `llm_generator.py`. You may need to provide more specific instructions or use a more capable model like GPT-4.

### Q: Database locked error (SQLite)
A: SQLite doesn't handle concurrent writes well. Use PostgreSQL for production.

## Best Practices

### Q: How often should I send tasks?
A: Space them out (e.g., one per week) to give students time and reduce costs.

### Q: Should I test tasks before sending?
A: Absolutely! Use `test_api.py` with your own endpoint first.

### Q: How do I prevent cheating?
A: The system generates unique tasks per student using seeds. Each student gets different parameters.

### Q: What's the best LLM model to use?
A: GPT-4 Turbo gives best results but costs more. GPT-3.5 Turbo is cheaper but may need more specific prompts.

### Q: How do I backup data?
A: Regularly backup your database:
```bash
# SQLite
cp deployment.db deployment.db.backup

# PostgreSQL
pg_dump dbname > backup.sql
```

