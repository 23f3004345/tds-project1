import openai
import anthropic
import requests
import config
import json
import base64
import re

class LLMGenerator:
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        if self.provider == 'openai':
            openai.api_key = config.OPENAI_API_KEY
            self.model = config.LLM_MODEL
        elif self.provider == 'anthropic':
            self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
            self.model = 'claude-3-sonnet-20240229'
        elif self.provider == 'iitm':
            self.token = config.IITM_AI_TOKEN
            self.api_base = config.IITM_API_BASE_URL
            self.model = config.LLM_MODEL
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }

    def _call_iitm_api(self, messages, max_tokens=4000, temperature=0.7):
        """Call the IIT Madras AI pipeline API."""
        # Try OpenAI-compatible format first
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            # Try the chat/completions endpoint (OpenAI-compatible)
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=config.REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            elif response.status_code == 404:
                # If chat/completions doesn't exist, try alternative endpoints
                print("Trying alternative IITM API endpoint...")

                # Try a simpler format that IIT Madras might use
                simple_payload = {
                    "prompt": messages[-1]["content"],  # Use the last user message
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }

                # Try /generate endpoint
                response = requests.post(
                    f"{self.api_base}/generate",
                    headers=self.headers,
                    json=simple_payload,
                    timeout=config.REQUEST_TIMEOUT
                )

                if response.status_code == 200:
                    result = response.json()
                    # Handle different response formats
                    if 'text' in result:
                        return result['text']
                    elif 'response' in result:
                        return result['response']
                    elif 'content' in result:
                        return result['content']
                    else:
                        return str(result)

            # If we get here, something went wrong
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f"Network error calling IITM API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            raise
        except Exception as e:
            print(f"Error calling IITM API: {e}")
            print(f"Response status: {response.status_code if 'response' in locals() else 'Unknown'}")
            print(f"Response text: {response.text if 'response' in locals() else 'Unknown'}")
            raise

    def generate_app(self, brief, checks, attachments=None):
        """Generate a complete application based on the brief and checks."""
        prompt = self._build_prompt(brief, checks, attachments)

        if self.provider == 'iitm':
            messages = [
                {"role": "system", "content": "You are an expert web developer. Generate production-ready, single-page HTML applications with inline CSS and JavaScript. Follow best practices and ensure all requirements are met."},
                {"role": "user", "content": prompt}
            ]
            code = self._call_iitm_api(messages, max_tokens=4000, temperature=0.7)
        elif self.provider == 'openai':
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert web developer. Generate production-ready, single-page HTML applications with inline CSS and JavaScript. Follow best practices and ensure all requirements are met."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            code = response.choices[0].message.content
        else:  # anthropic
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                system="You are an expert web developer. Generate production-ready, single-page HTML applications with inline CSS and JavaScript. Follow best practices and ensure all requirements are met."
            )
            code = message.content[0].text

        # Extract HTML from code blocks if present
        html_code = self._extract_html(code)
        return html_code

    def generate_readme(self, brief, task_id, repo_name):
        """Generate a professional README.md file."""
        prompt = f"""Generate a professional README.md for a web application with the following details:

Task: {task_id}
Repository: {repo_name}
Brief: {brief}

The README should include:
1. Project title and description
2. Features list
3. Setup instructions (if any)
4. Usage instructions
5. Code explanation (brief overview of how it works)
6. License (MIT)

Format it in proper Markdown with clear sections."""

        if self.provider == 'iitm':
            messages = [
                {"role": "system", "content": "You are a technical writer who creates clear, professional README files."},
                {"role": "user", "content": prompt}
            ]
            readme = self._call_iitm_api(messages, max_tokens=2000, temperature=0.7)
        elif self.provider == 'openai':
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical writer who creates clear, professional README files."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            readme = response.choices[0].message.content
        else:  # anthropic
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                system="You are a technical writer who creates clear, professional README files."
            )
            readme = message.content[0].text

        return readme

    def _build_prompt(self, brief, checks, attachments=None):
        """Build the prompt for app generation."""
        prompt = f"""Create a single-page HTML application that meets the following requirements:

BRIEF:
{brief}

CHECKS THAT MUST PASS:
"""
        for i, check in enumerate(checks, 1):
            prompt += f"{i}. {check}\n"

        if attachments:
            prompt += "\nATTACHMENTS:\n"
            for att in attachments:
                prompt += f"- {att['name']}: {att['url'][:100]}...\n"

        prompt += """

REQUIREMENTS:
1. Create a complete, self-contained HTML file with inline CSS and JavaScript
2. Use modern, clean design with responsive layout
3. Include all necessary CDN links for external libraries (Bootstrap, marked, highlight.js, etc.)
4. Ensure all element IDs and functionality match the checks exactly
5. Handle errors gracefully
6. Add appropriate comments in the code
7. Make it production-ready and professional

Return ONLY the complete HTML code, no explanations."""

        return prompt

    def _extract_html(self, content):
        """Extract HTML code from markdown code blocks if present."""
        # Try to find HTML in code blocks
        html_match = re.search(r'```html\n(.*?)\n```', content, re.DOTALL)
        if html_match:
            return html_match.group(1)

        # Try generic code blocks
        code_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
        if code_match:
            return code_match.group(1)

        # If no code blocks, check if it starts with HTML
        if content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html'):
            return content.strip()

        # Last resort: return as is
        return content

    def save_attachments_locally(self, attachments, output_dir):
        """Save data URI attachments to local files."""
        saved_files = []
        for att in attachments:
            if att['url'].startswith('data:'):
                # Parse data URI
                match = re.match(r'data:([^;]+);base64,(.+)', att['url'])
                if match:
                    mime_type, data = match.groups()
                    file_data = base64.b64decode(data)
                    file_path = f"{output_dir}/{att['name']}"
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    saved_files.append({'name': att['name'], 'path': file_path})
        return saved_files
