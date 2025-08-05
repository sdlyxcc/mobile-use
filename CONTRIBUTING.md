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

Yes — absolutely. What you have is based on a classic `pip-tools` or `poetry` workflow, but **it doesn't match how `uv` actually works**, and yes — you can **simplify it a lot** while still being precise.

## Dependency Management

We use [`uv`](https://github.com/astral-sh/uv) for dependency management and locking.

### 🔄 Installing dependencies

To install all project dependencies from the lockfile:

```bash
uv sync
```

````

This ensures a consistent environment across all machines.

---

### ➕ Adding a new package

To add a new package (dev or prod):

```bash
uv pip install <package-name>
uv lock
```

Then commit the updated `uv.lock`.

If the package is used only in development, add the `--extra=dev` flag:

```bash
uv pip install <package-name> --extra=dev
uv lock
```

---

### ✅ Keeping things in sync

If you update dependencies manually (or pull a new lockfile):

```bash
uv sync
```

That's it.
````
