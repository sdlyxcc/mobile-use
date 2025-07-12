# Contributing to MiniTap

First off, thank you for considering contributing to MiniTap! Your help is greatly appreciated.

## Getting Started

1.  **Fork & Clone**: Fork the repository and clone it to your local machine.
2.  **Set up Environment**: Follow README.md instructions to get started.

## Making Changes

1.  **Branching**: Create a new branch for your feature or bug fix from the `main` branch.
    ```bash
    git checkout -b your-feature-name
    ```
2.  **Code Style & Quality**: Before committing, please run our linter and formatter to ensure your code adheres to the project's style guidelines.

    ```bash
    # Check for any linting errors
    ruff check .

    # Automatically format your code
    ruff format .
    ```

3.  **Commit**: Use clear and descriptive commit messages, following conventional commits.

## Submitting a Pull Request

Once your changes are ready, push your branch to your fork and open a Pull Request against the `main` branch of the original repository. Provide a clear description of the changes you've made.

## Dependency Management

If you need to add a new package:

1.  **Add to `pyproject.toml`**: Add the package to the `dependencies` list (for the main project) or the `[project.optional-dependencies].dev` list (for development tools).
2.  **Update the Lock File**: Regenerate the `requirements.txt` file to lock the new set of dependencies. This ensures everyone uses the same versions.
    ```bash
    uv pip compile pyproject.toml -o requirements.txt
    ```
3.  **Commit Both Files**: Commit the changes to both `pyproject.toml` and the updated `requirements.txt`.
4.  **Update Your Environment**: Run the install command again to ensure your local environment reflects the changes.
    ```bash
    uv pip install -e ".[dev]"
    ```
