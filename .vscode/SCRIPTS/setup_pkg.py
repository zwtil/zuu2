import os
import sys

def create_python_package(pkg_name: str):
    # Create package directory structure
    if os.path.exists(os.path.join("PYTHON_PKG", pkg_name)):
        print(f"Package {pkg_name} already exists")
        return

    pkg_path = os.path.join("PYTHON_PKG", pkg_name)
    src_path = os.path.join(pkg_path, "src", "zuu", pkg_name)
    os.makedirs(src_path, exist_ok=True)

    # Create __init__.py in the package directory
    with open(os.path.join(src_path, "__init__.py"), "w") as f:
        pass

    # Create pyproject.toml
    pyproject_content = f'''[project]
name = "zuu-{pkg_name}"
version = "0.1.0"
description = "Add your description here"
authors = [
    {{ name = "ZackaryW", email = "36378555+ZackaryW@users.noreply.github.com" }}
]
dependencies = []
requires-python = ">= 3.8"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.rye]
managed = true
dev-dependencies = []

[tool.hatch.metadata]
allow-direct-references = true

[tool.hatch.build.targets.wheel]
packages = ["src/zuu"]
'''

    with open(os.path.join(pkg_path, "pyproject.toml"), "w") as f:
        f.write(pyproject_content)

    # Create workspace file
    workspace_content = f'''{{
    "folders": [
        {{
            "path": "../PYTHON_PKG/{pkg_name}"
        }}
    ],
    "settings": {{
        "files.exclude": {{
            "**/__pycache__": true,
            "**/*.pyc": true
        }},
        "python.analysis.extraPaths": [
            "."
        ]
    }}
}}'''

    workspace_path = os.path.join("WORKSPACES", f"py_zuu_{pkg_name}.code-workspace")
    with open(workspace_path, "w") as f:
        f.write(workspace_content)


if __name__ == "__main__":
    pkg_name = input("Enter the name of the package: ")
    assert pkg_name, "Package name cannot be empty"
    assert isinstance(pkg_name, str), "Package name must be a string"
    create_python_package(pkg_name)

