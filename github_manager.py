from github import Github, GithubException
import config
import time
import os

class GitHubManager:
    def __init__(self):
        self.github = Github(config.GITHUB_TOKEN)
        self.user = self.github.get_user()

    def create_repo(self, repo_name, description="Auto-generated application"):
        """Create a new GitHub repository."""
        try:
            repo = self.user.create_repo(
                repo_name,
                description=description,
                private=False,
                auto_init=False
            )
            print(f"Created repository: {repo.html_url}")
            return repo
        except GithubException as e:
            print(f"Error creating repo: {e}")
            raise

    def add_file(self, repo, file_path, content, commit_message):
        """Add a file to the repository."""
        try:
            repo.create_file(file_path, commit_message, content)
            print(f"Added file: {file_path}")
        except GithubException as e:
            print(f"Error adding file {file_path}: {e}")
            raise

    def add_license(self, repo):
        """Add MIT LICENSE to the repository."""
        license_content = """MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        self.add_file(repo, "LICENSE", license_content, "Add MIT LICENSE")

    def enable_pages(self, repo):
        """Enable GitHub Pages for the repository."""
        try:
            # Create gh-pages branch from main
            main_branch = repo.get_branch("main")
            repo.create_git_ref(
                ref=f"refs/heads/{config.PAGES_BRANCH}",
                sha=main_branch.commit.sha
            )

            # Enable Pages
            repo.create_pages_site(
                source={
                    "branch": config.PAGES_BRANCH,
                    "path": "/"
                }
            )

            pages_url = f"https://{config.GITHUB_USERNAME}.github.io/{repo.name}/"
            print(f"GitHub Pages enabled: {pages_url}")

            # Wait for Pages to be ready
            self._wait_for_pages(pages_url)

            return pages_url
        except GithubException as e:
            print(f"Error enabling Pages: {e}")
            # Pages might already be enabled, try to get URL
            try:
                pages_url = f"https://{config.GITHUB_USERNAME}.github.io/{repo.name}/"
                return pages_url
            except:
                raise

    def _wait_for_pages(self, pages_url, timeout=300):
        """Wait for GitHub Pages to become available."""
        import requests
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(pages_url, timeout=10)
                if response.status_code == 200:
                    print("GitHub Pages is ready!")
                    return True
            except:
                pass

            print("Waiting for GitHub Pages to be ready...")
            time.sleep(10)

        print("Warning: Timeout waiting for Pages, but continuing...")
        return False

    def get_latest_commit_sha(self, repo, branch="main"):
        """Get the latest commit SHA for a branch."""
        try:
            branch_obj = repo.get_branch(branch)
            return branch_obj.commit.sha
        except GithubException as e:
            print(f"Error getting commit SHA: {e}")
            raise

    def deploy_app(self, task_id, html_content, readme_content, attachments=None):
        """Deploy a complete application to GitHub."""
        # Generate unique repo name
        repo_name = f"task-{task_id}"

        # Create repository
        repo = self.create_repo(repo_name, f"Generated application for {task_id}")

        # Add LICENSE
        self.add_license(repo)

        # Add README
        self.add_file(repo, "README.md", readme_content, "Add README")

        # Add index.html
        self.add_file(repo, "index.html", html_content, "Add application")

        # Add attachments if any
        if attachments:
            for att in attachments:
                if 'content' in att:
                    self.add_file(repo, att['name'], att['content'], f"Add {att['name']}")

        # Enable GitHub Pages
        pages_url = self.enable_pages(repo)

        # Get commit SHA
        commit_sha = self.get_latest_commit_sha(repo)

        return {
            'repo_url': repo.html_url,
            'commit_sha': commit_sha,
            'pages_url': pages_url
        }

    def update_app(self, repo_name, html_content, readme_content, commit_message="Update application"):
        """Update an existing application."""
        try:
            repo = self.user.get_repo(repo_name)

            # Update index.html
            try:
                file = repo.get_contents("index.html")
                repo.update_file(file.path, commit_message, html_content, file.sha)
            except:
                self.add_file(repo, "index.html", html_content, commit_message)

            # Update README.md
            try:
                file = repo.get_contents("README.md")
                repo.update_file(file.path, "Update README", readme_content, file.sha)
            except:
                self.add_file(repo, "README.md", readme_content, "Update README")

            # Get new commit SHA
            commit_sha = self.get_latest_commit_sha(repo)

            pages_url = f"https://{config.GITHUB_USERNAME}.github.io/{repo_name}/"

            return {
                'repo_url': repo.html_url,
                'commit_sha': commit_sha,
                'pages_url': pages_url
            }
        except GithubException as e:
            print(f"Error updating app: {e}")
            raise

