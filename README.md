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

1.  **Install the recommended extensions**

This repository includes a list of recommended VS Code extensions in the `.vscode/extensions.json` file. When you open this project in VS Code, you will be prompted to install these extensions. They are highly recommended to ensure a consistent development experience and to take full advantage of the project's tooling (like Ruff).

2. **Configure the IDE Python interpreter & Ruff**

Create a `.vscode/settings.json` file and add the following configurations:

🪟 If you're on Windows, set:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe"
}
```

🐧 On macOS/Linux, set:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
}
```

And make sure to add this as well (not platform-specific) so that Ruff formats on save:

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": "always",
    "source.fixAll.ruff": "always"
  },
  "ruff.enable": true,
  "ruff.path": ["ruff"]
}
```
