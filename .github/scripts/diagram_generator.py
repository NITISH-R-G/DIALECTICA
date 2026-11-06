import os
import json


def generate_diagrams(root_dir="."):
    """Generate Mermaid diagrams from architecture JSON."""
    arch_path = os.path.join(root_dir, "architecture.json")
    if not os.path.exists(arch_path):
        print("Architecture file not found.")
        return

    with open(arch_path, "r") as f:
        arch = json.load(f)

    os.makedirs(os.path.join(root_dir, "diagrams"), exist_ok=True)

    # 1. Component Diagram (Internal Modules)
    mermaid_comp = ["graph TD"]

    def safe_id(path):
        return path.replace("/", "_").replace(".", "_").replace("-", "_")

    # Pre-compute available module base names and path parts for O(1) lookups
    module_lookup = {}
    for other_module in arch.get("modules", {}):
        # We index all parts of the module path to maintain the "naive match" behavior
        parts = other_module.replace("\\", "/").split("/")
        for part in parts:
            name = part.replace(".py", "")
            if name not in module_lookup:
                module_lookup[name] = []
            if other_module not in module_lookup[name]:
                module_lookup[name].append(other_module)

    for module, data in arch.get("modules", {}).items():
        mod_id = safe_id(module)
        mod_label = os.path.splitext(os.path.basename(module))[0]
        # Clickable node back to source
        mermaid_comp.append(f'    {mod_id}["{mod_label}"]')
        mermaid_comp.append(f'    click {mod_id} href "{module}" "Go to source"')

        # Draw edges for internal imports
        for imp in data.get("imports", []):
            imp_name = imp.split(".")[-1]
            # Use pre-computed dictionary for O(1) lookup
            for other_module in module_lookup.get(imp_name, []):
                other_id = safe_id(other_module)
                mermaid_comp.append(f"    {mod_id} --> {other_id}")

    with open(os.path.join(root_dir, "diagrams", "components.mermaid"), "w") as f:
        f.write("\n".join(mermaid_comp))

    # 2. Dependency Diagram
    mermaid_dep = ["graph LR"]
    app_node = "Project"
    mermaid_dep.append(f'    {app_node}["My Application"]')

    for fw in arch.get("frameworks", []):
        fw_node = fw.replace(" ", "_")
        mermaid_dep.append(f'    {app_node} --> {fw_node}["{fw}"]')
        mermaid_dep.append(
            f"    style {fw_node} fill:#f9f,stroke:#333,stroke-width:2px"
        )

    for dep in arch.get("dependencies", {}).get("python", []):
        dep_node = dep.replace("-", "_").replace("[", "_").replace("]", "_").split()[0]
        mermaid_dep.append(f'    {app_node} -.-> {dep_node}["{dep}"]')

    with open(os.path.join(root_dir, "diagrams", "dependencies.mermaid"), "w") as f:
        f.write("\n".join(mermaid_dep))

    print("Generated Mermaid diagrams in diagrams/ directory.")


if __name__ == "__main__":
    generate_diagrams()
