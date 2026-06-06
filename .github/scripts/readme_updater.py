import os
import json
import datetime

def update_readme(root_dir="."):
    arch_path = os.path.join(root_dir, "architecture.json")
    if not os.path.exists(arch_path):
        print("Architecture file not found. Skipping README update.")
        return

    with open(arch_path, "r") as f:
        arch = json.load(f)

    # Load diagrams
    comp_diagram = ""
    comp_path = os.path.join(root_dir, "diagrams", "components.mermaid")
    if os.path.exists(comp_path):
        with open(comp_path, "r") as f:
            comp_diagram = f.read()

    dep_diagram = ""
    dep_path = os.path.join(root_dir, "diagrams", "dependencies.mermaid")
    if os.path.exists(dep_path):
        with open(dep_path, "r") as f:
            dep_diagram = f.read()

    # Read original README title/header if it exists to preserve HuggingFace tags
    original_header = ""
    readme_path = os.path.join(root_dir, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            content = f.read()
            if content.startswith("---"):
                parts = content.split("---")
                if len(parts) >= 3:
                    original_header = "---" + parts[1] + "---\n\n"

    # Generate Markdown
    readme_content = f"""{original_header}# Project Documentation

> **Auto-generated Repository Status:** _Updated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}_

[![CI/CD Pipeline](https://github.com/OWNER/REPO/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci-cd.yml)
[![Repository Automation](https://github.com/OWNER/REPO/actions/workflows/repo-automation.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/repo-automation.yml)

## 📌 Project Overview
This repository uses the following core frameworks: {", ".join(arch.get("frameworks", ["Python"]))}

## 🏗️ System Architecture

### Component Map
Interactive view of internal modules and their relationships:
```mermaid
{comp_diagram}
```

### Dependency Map
```mermaid
{dep_diagram}
```

## 📦 Technology Stack
**Dependencies:**
{chr(10).join([f'- `{dep}`' for dep in arch.get("dependencies", {}).get("python", [])])}

## 📂 Repository Structure
**Entrypoints:**
{chr(10).join([f'- `[source]({ep})`' for ep in arch.get("entrypoints", [])])}

## ⚙️ Environment Variables
{chr(10).join([f'- `{var}`' for var in arch.get("env_vars", [])]) if arch.get("env_vars") else "No hardcoded env vars detected."}

## 🚀 Setup & Deployment Instructions
1. Clone the repository
2. Install dependencies: `pip install -e .[dev]`
3. Run tests: `pytest`
4. Run application: `uv run --project . server`

## 🤝 Contribution Guide
- Review PRs via the AI Documentation Agent.
- Linting and formatting run automatically via GitHub Actions (black, flake8).
- Ensure your changes do not break the dependency maps.

---
*This README is continuously updated by repository automation.*
"""

    with open(readme_path, "w") as f:
        f.write(readme_content)
    print("Updated README.md automatically.")

if __name__ == "__main__":
    update_readme()
