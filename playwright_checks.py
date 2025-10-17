from playwright.sync_api import sync_playwright
import time

class PlaywrightChecker:
    def __init__(self):
        self.playwright = None
        self.browser = None

    def start(self):
        """Start Playwright browser."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)

    def stop(self):
        """Stop Playwright browser."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def run_checks(self, pages_url, checks, timeout=15000):
        """Run JavaScript checks on the deployed page."""
        if not self.browser:
            self.start()

        results = []
        page = self.browser.new_page()

        try:
            # Navigate to page
            print(f"Loading page: {pages_url}")
            page.goto(pages_url, wait_until='networkidle', timeout=timeout)

            # Wait a bit for dynamic content
            time.sleep(2)

            # Run each check
            for i, check in enumerate(checks):
                check_result = {
                    'check': check,
                    'passed': False,
                    'error': None
                }

                try:
                    # Extract JavaScript code from check
                    if check.startswith('js:'):
                        js_code = check[3:].strip()
                    else:
                        js_code = check

                    # Execute JavaScript
                    result = page.evaluate(js_code)

                    # Check if result is truthy
                    check_result['passed'] = bool(result)
                    check_result['result'] = result

                    status = "✓" if check_result['passed'] else "✗"
                    print(f"  {status} Check {i+1}: {check[:80]}...")

                except Exception as e:
                    check_result['error'] = str(e)
                    print(f"  ✗ Check {i+1} failed: {e}")

                results.append(check_result)

        except Exception as e:
            print(f"Error loading page: {e}")
            results.append({
                'check': 'Page load',
                'passed': False,
                'error': str(e)
            })

        finally:
            page.close()

        return results

    def screenshot(self, pages_url, output_path):
        """Take a screenshot of the page."""
        if not self.browser:
            self.start()

        page = self.browser.new_page()
        try:
            page.goto(pages_url, wait_until='networkidle')
            page.screenshot(path=output_path, full_page=True)
            print(f"Screenshot saved to {output_path}")
        finally:
            page.close()

