import os
from dotenv import load_dotenv

load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')

# LLM Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
IITM_AI_TOKEN = os.getenv('IITM_AI_TOKEN')
IITM_API_BASE_URL = os.getenv('IITM_API_BASE_URL', 'https://api.iitm.ac.in/ai/v1')
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'iitm')  # Default to iitm
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4-turbo-preview')

# Student Configuration
STUDENT_SECRET = os.getenv('STUDENT_SECRET')
STUDENT_EMAIL = os.getenv('STUDENT_EMAIL')

# API Configuration
API_PORT = int(os.getenv('API_PORT', 5000))
STUDENT_API_BASE_URL = os.getenv('STUDENT_API_BASE_URL', 'http://localhost:5000')
EVALUATION_API_BASE_URL = os.getenv('EVALUATION_API_BASE_URL', 'http://localhost:5001')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///deployment.db')

# Timeouts and Retry Configuration
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 600))  # 10 minutes
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 5))
RETRY_DELAYS = [1, 2, 4, 8, 16]  # Exponential backoff in seconds

# GitHub Pages Configuration
PAGES_BRANCH = 'gh-pages'
PAGES_CHECK_TIMEOUT = 300  # 5 minutes to wait for Pages to be ready
