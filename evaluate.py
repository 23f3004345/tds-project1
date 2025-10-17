import requests
import json
import ast
from datetime import datetime
from models import SessionLocal, Repo, Result, Task
from playwright_checks import PlaywrightChecker
from github import Github
import config
import openai

def check_license(repo_url, commit_sha):
    """Check if repo has MIT LICENSE."""
    try:
        # Parse repo from URL
        parts = repo_url.rstrip('/').split('/')
        owner, repo_name = parts[-2], parts[-1]

        # Get LICENSE file
        github = Github(config.GITHUB_TOKEN)
        repo = github.get_repo(f"{owner}/{repo_name}")

        try:
            license_file = repo.get_contents("LICENSE", ref=commit_sha)
            content = license_file.decoded_content.decode('utf-8')

            # Check if it's MIT
            is_mit = 'MIT' in content and 'Permission is hereby granted' in content
            return {
                'score': 1.0 if is_mit else 0.0,
                'reason': 'MIT LICENSE found' if is_mit else 'LICENSE exists but not MIT',
                'logs': content[:200]
            }
        except:
            return {
                'score': 0.0,
                'reason': 'No LICENSE file found',
                'logs': ''
            }
    except Exception as e:
        return {
            'score': 0.0,
            'reason': f'Error checking license: {str(e)}',
            'logs': ''
        }

def check_readme_quality(repo_url, commit_sha):
    """Use LLM to evaluate README quality."""
    try:
        # Parse repo from URL
        parts = repo_url.rstrip('/').split('/')
        owner, repo_name = parts[-2], parts[-1]

        # Get README file
        github = Github(config.GITHUB_TOKEN)
        repo = github.get_repo(f"{owner}/{repo_name}")

        try:
            readme_file = repo.get_contents("README.md", ref=commit_sha)
            readme_content = readme_file.decoded_content.decode('utf-8')
        except:
            return {
                'score': 0.0,
                'reason': 'No README.md found',
                'logs': ''
            }

        # Evaluate with LLM
        prompt = f"""Evaluate the quality of this README.md file on a scale of 0-10.

README Content:
{readme_content}

Criteria:
- Has clear title and description
- Includes setup/usage instructions
- Has code explanation
- Mentions license
- Professional formatting
- Well-organized

Respond with ONLY a JSON object in this format:
{{"score": 0-10, "reason": "brief explanation"}}"""

        if config.LLM_PROVIDER == 'openai':
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            result_text = response.choices[0].message.content
        else:
            import anthropic
            client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
            message = client.messages.create(
                model='claude-3-haiku-20240307',
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            result_text = message.content[0].text

        # Parse JSON response
        result = json.loads(result_text.strip())

        return {
            'score': result['score'] / 10.0,  # Normalize to 0-1
            'reason': result['reason'],
            'logs': readme_content[:500]
        }
    except Exception as e:
        return {
            'score': 0.0,
            'reason': f'Error evaluating README: {str(e)}',
            'logs': ''
        }

def check_code_quality(repo_url, commit_sha):
    """Use LLM to evaluate code quality."""
    try:
        # Parse repo from URL
        parts = repo_url.rstrip('/').split('/')
        owner, repo_name = parts[-2], parts[-1]

        # Get index.html file
        github = Github(config.GITHUB_TOKEN)
        repo = github.get_repo(f"{owner}/{repo_name}")

        try:
            code_file = repo.get_contents("index.html", ref=commit_sha)
            code_content = code_file.decoded_content.decode('utf-8')
        except:
            return {
                'score': 0.0,
                'reason': 'No index.html found',
                'logs': ''
            }

        # Evaluate with LLM
        prompt = f"""Evaluate the quality of this HTML/CSS/JavaScript code on a scale of 0-10.

Code:
{code_content[:3000]}

Criteria:
- Clean, readable code
- Proper structure
- Good practices
- Comments where needed
- Error handling
- Responsive design

Respond with ONLY a JSON object in this format:
{{"score": 0-10, "reason": "brief explanation"}}"""

        if config.LLM_PROVIDER == 'openai':
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            result_text = response.choices[0].message.content
        else:
            import anthropic
            client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
            message = client.messages.create(
                model='claude-3-haiku-20240307',
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            result_text = message.content[0].text

        # Parse JSON response
        result = json.loads(result_text.strip())

        return {
            'score': result['score'] / 10.0,  # Normalize to 0-1
            'reason': result['reason'],
            'logs': code_content[:500]
        }
    except Exception as e:
        return {
            'score': 0.0,
            'reason': f'Error evaluating code: {str(e)}',
            'logs': ''
        }

def check_repo_timing(repo, task):
    """Check if repo was created after task request."""
    try:
        # Parse repo from URL
        parts = repo.repo_url.rstrip('/').split('/')
        owner, repo_name = parts[-2], parts[-1]

        github = Github(config.GITHUB_TOKEN)
        gh_repo = github.get_repo(f"{owner}/{repo_name}")

        created_at = gh_repo.created_at
        task_time = task.timestamp

        is_valid = created_at > task_time

        return {
            'score': 1.0 if is_valid else 0.0,
            'reason': f'Repo created at {created_at}, task sent at {task_time}',
            'logs': f'Created: {created_at}, Task: {task_time}'
        }
    except Exception as e:
        return {
            'score': 0.0,
            'reason': f'Error checking timing: {str(e)}',
            'logs': ''
        }

def evaluate_submission(repo):
    """Evaluate a single submission."""
    db = SessionLocal()

    try:
        print(f"\nEvaluating: {repo.email} - {repo.task} (Round {repo.round})")
        print(f"Repo: {repo.repo_url}")
        print(f"Pages: {repo.pages_url}")

        # Get task details
        task = db.query(Task).filter_by(
            email=repo.email,
            task=repo.task,
            round=repo.round
        ).first()

        if not task:
            print("  ✗ Task not found")
            return

        # Parse checks from task
        try:
            checks = ast.literal_eval(task.checks)
        except:
            checks = json.loads(task.checks)

        results_to_save = []

        # 1. Check repo timing
        print("  Checking repo creation timing...")
        timing_result = check_repo_timing(repo, task)
        results_to_save.append(('Repo created after task', timing_result))

        # 2. Check LICENSE
        print("  Checking LICENSE...")
        license_result = check_license(repo.repo_url, repo.commit_sha)
        results_to_save.append(('MIT LICENSE present', license_result))

        # 3. Check README quality
        print("  Evaluating README quality...")
        readme_result = check_readme_quality(repo.repo_url, repo.commit_sha)
        results_to_save.append(('README quality', readme_result))

        # 4. Check code quality
        print("  Evaluating code quality...")
        code_result = check_code_quality(repo.repo_url, repo.commit_sha)
        results_to_save.append(('Code quality', code_result))

        # 5. Run Playwright checks
        print("  Running dynamic checks with Playwright...")
        checker = PlaywrightChecker()
        try:
            playwright_results = checker.run_checks(repo.pages_url, checks)
            for i, pr in enumerate(playwright_results):
                check_name = f"Functional check {i+1}"
                results_to_save.append((
                    check_name,
                    {
                        'score': 1.0 if pr['passed'] else 0.0,
                        'reason': pr.get('error', 'Passed' if pr['passed'] else 'Failed'),
                        'logs': pr.get('check', '')
                    }
                ))
        finally:
            checker.stop()

        # Save all results to database
        for check_name, result in results_to_save:
            db_result = Result(
                timestamp=datetime.utcnow(),
                email=repo.email,
                task=repo.task,
                round=repo.round,
                repo_url=repo.repo_url,
                commit_sha=repo.commit_sha,
                pages_url=repo.pages_url,
                check=check_name,
                score=result['score'],
                reason=result['reason'],
                logs=result['logs']
            )
            db.add(db_result)

        db.commit()

        # Calculate overall score
        total_score = sum(r[1]['score'] for r in results_to_save)
        max_score = len(results_to_save)
        percentage = (total_score / max_score * 100) if max_score > 0 else 0

        print(f"  Overall Score: {total_score:.1f}/{max_score} ({percentage:.1f}%)")

    finally:
        db.close()

def evaluate_all():
    """Evaluate all submissions that haven't been evaluated yet."""
    db = SessionLocal()

    try:
        # Get all repos
        repos = db.query(Repo).all()

        print(f"Found {len(repos)} submissions to evaluate\n")

        for repo in repos:
            # Check if already evaluated
            existing = db.query(Result).filter_by(
                email=repo.email,
                task=repo.task,
                round=repo.round
            ).first()

            if existing:
                print(f"✓ {repo.email} - {repo.task} (Round {repo.round}): Already evaluated")
                continue

            evaluate_submission(repo)

        print("\n" + "="*60)
        print("Evaluation complete!")
        print("="*60)

    finally:
        db.close()

if __name__ == "__main__":
    openai.api_key = config.OPENAI_API_KEY
    evaluate_all()

