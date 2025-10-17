"""
Test script to verify the student API works correctly.
"""
import requests
import json

def test_student_api():
    """Test the student API with a sample request."""

    url = "http://localhost:5000/api/deploy"

    # Sample task request
    test_request = {
        "email": "test@example.com",
        "secret": "my-secure-secret-123",  # Should match .env STUDENT_SECRET
        "task": "sum-of-sales-test1",
        "round": 1,
        "nonce": "test-nonce-12345",
        "brief": "Publish a single-page site that displays 'Hello World' in an h1 tag with id='greeting' and uses Bootstrap 5 from jsdelivr.",
        "checks": [
            "js: document.querySelector('#greeting').textContent === 'Hello World'",
            "js: !!document.querySelector(\"link[href*='bootstrap']\")"
        ],
        "attachments": [],
        "evaluation_url": "http://localhost:5001/api/notify"
    }

    print("Testing Student API...")
    print(f"URL: {url}")
    print(f"Request: {json.dumps(test_request, indent=2)}\n")

    try:
        response = requests.post(
            url,
            json=test_request,
            headers={'Content-Type': 'application/json'},
            timeout=300
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✓ Test PASSED!")
            result = response.json()
            if 'repo_url' in result:
                print(f"\nGenerated Repository: {result['repo_url']}")
            if 'pages_url' in result:
                print(f"GitHub Pages: {result['pages_url']}")
        else:
            print("\n✗ Test FAILED!")

    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Could not connect to API. Make sure student_api.py is running.")
    except Exception as e:
        print(f"✗ ERROR: {e}")

if __name__ == "__main__":
    test_student_api()

