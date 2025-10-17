# LLM Code Deployment System

A comprehensive system for building, deploying, and evaluating student applications using LLM-assisted code generation and automated testing.

## Overview

This project consists of three main components:

1. **Student API Endpoint** - Receives task requests, generates apps using LLMs, and deploys to GitHub Pages
2. **Evaluation System** - Receives deployment notifications and runs automated checks
3. **Task Management** - Generates and distributes tasks to students

## Features

- Automated app generation using LLM
- GitHub repository creation and deployment
- GitHub Pages hosting
- Automated evaluation (static, dynamic, LLM-based)
- Round-based revision system
- Task templating and parameterization

## Setup

### Prerequisites

- Python 3.8+
- Node.js 16+ (for Playwright)
- GitHub Personal Access Token
- OpenAI API Key or other LLM provider
- Database (PostgreSQL recommended)

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### Configuration

Create a `.env` file:

```env
# GitHub
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_username

# LLM Provider
OPENAI_API_KEY=your_openai_key

# Student Secret
STUDENT_SECRET=your_secret_here

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# API Settings
API_PORT=5000
STUDENT_API_BASE_URL=https://your-domain.com
```

## Usage

### For Students

1. **Start the API endpoint:**
```bash
python student_api.py
```

2. **Submit your endpoint URL and secret** via the Google Form

3. **Wait for task requests** - The system will automatically:
   - Receive the task
   - Generate the app using LLM
   - Create a GitHub repo
   - Deploy to GitHub Pages
   - Notify the evaluation system

### For Instructors

1. **Initialize the database:**
```bash
python init_db.py
```

2. **Start the evaluation API:**
```bash
python evaluation_api.py
```

3. **Run Round 1 tasks:**
```bash
python round1.py --submissions submissions.csv
```

4. **Run evaluations:**
```bash
python evaluate.py
```

5. **Run Round 2 tasks:**
```bash
python round2.py
```

## Project Structure

```
├── student_api.py          # Student API endpoint
├── evaluation_api.py       # Evaluation webhook endpoint
├── round1.py              # Round 1 task generator
├── round2.py              # Round 2 task generator
├── evaluate.py            # Automated evaluation script
├── init_db.py             # Database initialization
├── config.py              # Configuration management
├── models.py              # Database models
├── llm_generator.py       # LLM-based app generator
├── github_manager.py      # GitHub operations
├── task_templates.py      # Task templates
├── playwright_checks.py   # Dynamic testing
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Code Explanation

### Student API (`student_api.py`)
- Validates incoming requests with secret verification
- Parses task briefs and attachments
- Uses LLM to generate application code
- Creates GitHub repository and pushes code
- Enables GitHub Pages
- Notifies evaluation system

### LLM Generator (`llm_generator.py`)
- Processes task briefs and checks
- Generates HTML/CSS/JavaScript code
- Handles attachments (data URIs)
- Creates professional README files
- Ensures code quality and best practices

### GitHub Manager (`github_manager.py`)
- Creates repositories with unique names
- Adds MIT LICENSE
- Pushes code and commits
- Enables GitHub Pages
- Manages repository settings

### Evaluation System (`evaluation_api.py`, `evaluate.py`)
- Receives deployment notifications
- Validates submission timing
- Runs static checks (LICENSE, README)
- Uses LLM for code quality assessment
- Executes Playwright tests for dynamic checks
- Stores results in database

### Task Management (`round1.py`, `round2.py`)
- Generates unique tasks from templates
- Parameterizes with seeds for randomization
- Tracks task distribution
- Manages round progression

## License

MIT License - See LICENSE file for details

