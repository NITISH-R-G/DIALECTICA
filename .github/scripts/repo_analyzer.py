import os
import ast
import json

def analyze_repo(root_dir="."):
    """Analyze the repository and build an architecture model."""
    architecture = {
        "frameworks": [],
        "dependencies": {},
        "modules": {},
        "entrypoints": [],
        "env_vars": []
    }

    # Extract info from pyproject.toml
    toml_path = os.path.join(root_dir, "pyproject.toml")
    if os.path.exists(toml_path):
        with open(toml_path, "r") as f:
            content = f.read()
            if "fastapi" in content.lower():
                architecture["frameworks"].append("FastAPI")
            if "openenv" in content.lower():
                architecture["frameworks"].append("OpenEnv")

            # Basic dependency parsing (very simplified)
            in_deps = False
            deps = []
            for line in content.split("\n"):
                if line.strip().startswith("dependencies = ["):
                    in_deps = True
                    continue
                if in_deps and line.strip() == "]":
                    in_deps = False
                if in_deps and line.strip() and not line.strip().startswith("#"):
                    deps.append(line.strip().strip('",').split(">=")[0].split("==")[0].split("@")[0].strip('"').strip())
            architecture["dependencies"]["python"] = [d for d in deps if d]

    # Analyze Python files using AST
    for subdir, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", ".venv", ".github", "node_modules"]]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(subdir, file)
                rel_path = os.path.relpath(filepath, root_dir)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())

                    imports = []
                    functions = []
                    classes = []

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.append(node.module)
                        elif isinstance(node, ast.FunctionDef):
                            functions.append(node.name)
                        elif isinstance(node, ast.ClassDef):
                            classes.append(node.name)

                        # Detect environment variables
                        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                            if node.func.attr == 'getenv' and getattr(node.func.value, 'id', '') == 'os':
                                if node.args and isinstance(node.args[0], ast.Constant):
                                    architecture["env_vars"].append(node.args[0].value)

                    architecture["modules"][rel_path] = {
                        "imports": imports,
                        "functions": functions,
                        "classes": classes
                    }

                    if "app" in file or "server" in file or "main" in file:
                        architecture["entrypoints"].append(rel_path)

                except Exception as e:
                    print(f"Failed to parse {rel_path}: {e}")

    architecture["env_vars"] = list(set(architecture["env_vars"]))

    # Save results
    with open(os.path.join(root_dir, "architecture.json"), "w") as f:
        json.dump(architecture, f, indent=2)

if __name__ == "__main__":
    analyze_repo()
