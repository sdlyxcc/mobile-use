# Project Setup

1. **Create & activate the virtual environment**

   ```bash
   uv venv                # uv reads .python-version → uses Python 3.12.2
   # macOS/Linux:
   source .venv/bin/activate

   # Windows:
   .venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   # Install project dependencies
   uv pip install -r requirements.txt
   # Install dev dependencies
   uv pip install -e ".[dev]"
   # Install & link the project
   uv pip install -e .
   ```

3. **Run the project**

   ```bash
   minitap --help
   ```

4. **Exit the virtual environment**

   ```bash
   deactivate
   ```

## Recommended VS Code Setup

This repository includes a list of recommended VS Code extensions in the `.vscode/extensions.json` file. When you open this project in VS Code, you will be prompted to install these extensions. They are highly recommended to ensure a consistent development experience and to take full advantage of the project's tooling (like Ruff).
