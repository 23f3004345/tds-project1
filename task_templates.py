        # Generate task ID
        task_id = generate_task_id(template['id'], brief, attachments)
    else:
        # Round 2: Pick a random round2 variant
        if not existing_task_id:
            raise ValueError("existing_task_id required for round 2")

        task_id = existing_task_id
        round2_variant = random.choice(template['round2'])
        brief = round2_variant['brief'].format(seed=seed)

        # Add attachments if specified
        attachments = []
        if 'attachments' in round2_variant:
            attachments = round2_variant['attachments'](seed)

        checks = [check.format(seed=seed, result=12345.67) for check in round2_variant['checks']]

    return {
        'template_id': template['id'],
        'task_id': task_id,
        'brief': brief,
        'attachments': attachments,
        'checks': checks
    }
import hashlib
import json
import random
from datetime import datetime

# Task templates as specified in the requirements
TASK_TEMPLATES = [
    {
        "id": "sum-of-sales",
        "brief_template": "Publish a single-page site that fetches data.csv from attachments, sums its sales column, sets the title to \"Sales Summary {seed}\", displays the total inside #total-sales, and loads Bootstrap 5 from jsdelivr.",
        "attachments_generator": lambda seed: [
            {
                "name": "data.csv",
                "url": generate_csv_data_uri(seed)
            }
        ],
        "checks_template": [
            "js: document.title === `Sales Summary {seed}`",
            "js: !!document.querySelector(\"link[href*='bootstrap']\")",
            "js: Math.abs(parseFloat(document.querySelector(\"#total-sales\").textContent) - {result}) < 0.01"
        ],
        "round2": [
            {
                "brief": "Add a Bootstrap table #product-sales that lists each product with its total sales and keeps #total-sales accurate after render.",
                "checks": [
                    "js: document.querySelectorAll(\"#product-sales tbody tr\").length >= 1",
                    "js: (() => { const rows = [...document.querySelectorAll(\"#product-sales tbody tr td:last-child\")]; const sum = rows.reduce((acc, cell) => acc + parseFloat(cell.textContent), 0); return Math.abs(sum - {result}) < 0.01; })()"
                ]
            },
            {
                "brief": "Introduce a currency select #currency-picker that converts the computed total using rates.json from attachments and mirrors the active currency inside #total-currency.",
                "attachments": lambda seed: [{"name": "rates.json", "url": generate_rates_data_uri(seed)}],
                "checks": [
                    "js: !!document.querySelector(\"#currency-picker option[value='USD']\")",
                    "js: !!document.querySelector(\"#total-currency\")"
                ]
            },
            {
                "brief": "Allow filtering by region via #region-filter, update #total-sales with the filtered sum, and set data-region on that element to the active choice.",
                "checks": [
                    "js: document.querySelector(\"#region-filter\").tagName === \"SELECT\"",
                    "js: document.querySelector(\"#total-sales\").dataset.region !== undefined"
                ]
            }
        ]
    },
    {
        "id": "markdown-to-html",
        "brief_template": "Publish a static page that converts input.md from attachments to HTML with marked, renders it inside #markdown-output, and loads highlight.js for code blocks.",
        "attachments_generator": lambda seed: [
            {
                "name": "input.md",
                "url": generate_markdown_data_uri(seed)
            }
        ],
        "checks_template": [
            "js: !!document.querySelector(\"script[src*='marked']\")",
            "js: !!document.querySelector(\"script[src*='highlight.js']\")",
            "js: document.querySelector(\"#markdown-output\").innerHTML.includes(\"<h\")"
        ],
        "round2": [
            {
                "brief": "Add tabs #markdown-tabs that switch between rendered HTML in #markdown-output and the original Markdown in #markdown-source while keeping content in sync.",
                "checks": [
                    "js: document.querySelectorAll(\"#markdown-tabs button\").length >= 2",
                    "js: document.querySelector(\"#markdown-source\").textContent.trim().length > 0"
                ]
            },
            {
                "brief": "Support loading Markdown from a ?url= parameter when present and fall back to the attachment otherwise, showing the active source in #markdown-source-label.",
                "checks": [
                    "js: document.querySelector(\"#markdown-source-label\").textContent.length > 0",
                    "js: !!document.querySelector(\"script\").textContent.includes(\"fetch(\")"
                ]
            },
            {
                "brief": "Display a live word count badge #markdown-word-count that updates after every render and formats numbers with Intl.NumberFormat.",
                "checks": [
                    "js: document.querySelector(\"#markdown-word-count\").textContent.includes(\",\")",
                    "js: !!document.querySelector(\"script\").textContent.includes(\"Intl.NumberFormat\")"
                ]
            }
        ]
    },
    {
        "id": "github-user-created",
        "brief_template": "Publish a Bootstrap page with form id=\"github-user-{seed}\" that fetches a GitHub username, optionally uses ?token=, and displays the account creation date in YYYY-MM-DD UTC inside #github-created-at.",
        "attachments_generator": lambda seed: [],
        "checks_template": [
            "js: document.querySelector(\"#github-user-{seed}\").tagName === \"FORM\"",
            "js: document.querySelector(\"#github-created-at\").textContent.includes(\"20\")",
            "js: !!document.querySelector(\"script\").textContent.includes(\"https://api.github.com/users/\")"
        ],
        "round2": [
            {
                "brief": "Show an aria-live alert #github-status that reports when a lookup starts, succeeds, or fails.",
                "checks": [
                    "js: document.querySelector(\"#github-status\").getAttribute(\"aria-live\") === \"polite\"",
                    "js: !!document.querySelector(\"script\").textContent.includes(\"github-status\")"
                ]
            },
            {
                "brief": "Display the account age in whole years inside #github-account-age alongside the creation date.",
                "checks": [
                    "js: parseInt(document.querySelector(\"#github-account-age\").textContent, 10) >= 0",
                    "js: document.querySelector(\"#github-account-age\").textContent.toLowerCase().includes(\"years\")"
                ]
            },
            {
                "brief": "Cache the last successful lookup in localStorage under \"github-user-{seed}\" and repopulate the form on load.",
                "checks": [
                    "js: !!document.querySelector(\"script\").textContent.includes(\"localStorage.setItem(\\\"github-user-{seed}\\\"\")",
                    "js: !!document.querySelector(\"script\").textContent.includes(\"localStorage.getItem(\\\"github-user-{seed}\\\"\")"
                ]
            }
        ]
    }
]

def generate_seed(email, date_str):
    """Generate a seed from email and date."""
    combined = f"{email}-{date_str}"
    return hashlib.sha256(combined.encode()).hexdigest()[:8]

def generate_task_id(template_id, brief, attachments):
    """Generate unique task ID."""
    data = json.dumps({"brief": brief, "attachments": attachments}, sort_keys=True)
    hash_val = hashlib.sha256(data.encode()).hexdigest()[:5]
    return f"{template_id}-{hash_val}"

def generate_csv_data_uri(seed):
    """Generate a CSV data URI with sales data."""
    random.seed(seed)
    products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
    regions = ["North", "South", "East", "West"]

    csv_lines = ["product,region,sales"]
    for _ in range(10):
        product = random.choice(products)
        region = random.choice(regions)
        sales = round(random.uniform(100, 1000), 2)
        csv_lines.append(f"{product},{region},{sales}")

    csv_content = "\n".join(csv_lines)
    import base64
    encoded = base64.b64encode(csv_content.encode()).decode()
    return f"data:text/csv;base64,{encoded}"

def generate_markdown_data_uri(seed):
    """Generate a Markdown data URI."""
    random.seed(seed)
    markdown_content = f"""# Sample Document {seed}

This is a sample markdown document with seed {seed}.

## Features

- Code highlighting
- **Bold text**
- *Italic text*

## Code Example

```python
def hello():
    print("Hello, World!")
```

## Conclusion

This is generated content for testing.
"""
    import base64
    encoded = base64.b64encode(markdown_content.encode()).decode()
    return f"data:text/markdown;base64,{encoded}"

def generate_rates_data_uri(seed):
    """Generate currency rates JSON data URI."""
    random.seed(seed)
    rates = {
        "USD": 1.0,
        "EUR": round(random.uniform(0.8, 0.9), 4),
        "GBP": round(random.uniform(0.7, 0.8), 4),
        "JPY": round(random.uniform(110, 130), 2)
    }
    import base64
    encoded = base64.b64encode(json.dumps(rates).encode()).decode()
    return f"data:application/json;base64,{encoded}"

def generate_task(email, template_id=None, round_num=1, existing_task_id=None):
    """Generate a task from templates."""
    # Select template
    if template_id:
        template = next((t for t in TASK_TEMPLATES if t['id'] == template_id), None)
        if not template:
            raise ValueError(f"Template {template_id} not found")
    else:
        template = random.choice(TASK_TEMPLATES)

    # Generate seed
    date_str = datetime.utcnow().strftime("%Y-%m-%d-%H")
    seed = generate_seed(email, date_str)

    if round_num == 1:
        # Round 1: Use main template
        brief = template['brief_template'].format(seed=seed)
        attachments = template['attachments_generator'](seed) if 'attachments_generator' in template else []
        checks = [check.format(seed=seed, result=12345.67) for check in template['checks_template']]


