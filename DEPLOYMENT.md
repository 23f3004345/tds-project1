# TDS Project 1 - LLM Code Deployment System

## Deployment Instructions

This Flask API is deployed on Render.com and provides automated code generation and GitHub Pages deployment.

## Environment Variables Required

Set these environment variables in your Render.com dashboard:

```
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=23f3004345
LLM_PROVIDER=iitm
IITM_AI_TOKEN=your_iitm_token
LLM_MODEL=gpt-4-turbo-preview
IITM_API_BASE_URL=https://llm.iitm.ac.in/v1
STUDENT_SECRET=my-secure-secret-123
STUDENT_EMAIL=23f3004345@ds.study.iitm.ac.in
API_PORT=5000
DATABASE_URL=sqlite:///deployment.db
REQUEST_TIMEOUT=600
MAX_RETRIES=5
```

## API Endpoints

- `GET /` - API information and documentation
- `GET /health` - Health check endpoint
- `POST /api/deploy` - Main deployment endpoint for task requests

## Local Development

```bash
pip install -r requirements.txt
python student_api.py
```

## Production Deployment

This app is configured for deployment on Render.com with:
- `Procfile` - Defines the web server command
- `runtime.txt` - Specifies Python version
- `requirements.txt` - Lists all dependencies

