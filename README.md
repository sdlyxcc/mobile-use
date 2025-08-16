# mobile-use: automate your phone with natural language

<p align="center">
  <img src="./doc/readme-banner-1280x320.png" alt="Project banner" />
</p>

### TL;DR

**What is it?** An AI agent to control your phone (IOS/Android) with natural language.

**How to run?**

- Either plug your Android device and enable USB-debugging
- Either launch an IOS/Android emulator

Then run in your terminal:

```bash
# 1. Build the Docker image
docker build -t mobile-use .

# 2. Run the agent to scrape data from your device
# (Ensure your device is connected and accessible via adb + env var set)
docker run --rm -it --env-file .env -e ADB_CONNECT_ADDR="host.docker.internal:5555" mobile-use \
  "Open Gmail, find first 3 unread emails, and list their sender and subject line" \
  --output-description "A JSON list of objects, each with 'sender' and 'subject' keys"
```

<div align="center">

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

## 💡 What is mobile-use?

Mobile-use is a powerful, open-source AI agent that controls your Android or IOS device using natural language. It understands your commands and interacts with the UI to perform tasks, from sending messages to navigating complex apps.

![mobile-use in Action](./doc/linkedin-demo.gif)

## ✨ Features

- **Natural Language Control**: Interact with your phone using your native language.
- **UI-Aware Automation**: Intelligently navigates through app interfaces.
- **Data Scraping**: Extract information from any app and structure it into your desired format (e.g., JSON) using a natural language description.
- **Extensible & Customizable**: Easily configure different LLMs to power the agents that power mobile-use.

## 🚀 Getting Started

Ready to automate your mobile experience? Follow these steps to get mobile-use up and running.

### Quick Launch (Docker)

For the fastest way to get started, please see the [TL;DR](#tldr) section at the top of this document for a one-command Docker setup.

### Manual Launch (Development Mode)

For developers who want to set up the environment manually:

#### 1. Device Support

Mobile-use currently supports the following devices:

- **Physical Android Phones**: Connect via USB with USB debugging enabled.
- **Android Simulators**: Set up through Android Studio.
- **iOS Simulators**: Supported for macOS users.

> **Note**: Physical iOS devices are not yet supported.

#### 2. Prerequisites

Before you begin, ensure you have the following installed:

- **[uv](https://github.com/astral-sh/uv)**: A lightning-fast Python package manager.
- **[Maestro](https://maestro.mobile.dev/getting-started/installing-maestro)**: The framework we use to interact with your device.

#### 3. Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/mobile-use.git
    cd mobile-use/mobile-use
    ```

2.  **Create & activate the virtual environment:**

    ```bash
    # This will create a .venv directory using the Python version in .python-version
    uv venv

    # Activate the environment
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows:
    .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    # Sync with the locked dependencies for a consistent setup
    uv sync
    ```

### 3. Configuration

1.  **Set up Environment Variables:**
    Copy the example `.env.example` file to `.env` and add your API keys. An OpenAI key is required for out-of-the-box functionality.

    ```bash
    cp .env.example .env
    ```

2.  **(Optional) Customize LLM Configuration:**
    To use different models or providers, create your own LLM configuration file.
    ```bash
    cp llm-config.override.template.jsonc llm-config.override.jsonc
    ```
    Then, edit `llm-config.override.jsonc` to fit your needs.

## 👨‍💻 Usage

To run mobile-use, simply pass your command as an argument.

**Example 1: Basic Command**

```bash
python ./src/mobile-use/main.py "Go to settings and tell me my current battery level"
```

**Example 2: Data Scraping**

Extract specific information and get it back in a structured format. For instance, to get a list of your unread emails:

```bash
python ./src/mobile-use/main.py \
  "Open Gmail, find all unread emails, and list their sender and subject line" \
  --output-description "A JSON list of objects, each with 'sender' and 'subject' keys"
```

> 💡 **Note:** If you haven't configured a specific model, mobile-use will prompt you to choose one from the available options.

## ❤️ Contributing

We love contributions! Whether you're fixing a bug, adding a feature, or improving documentation, your help is welcome. Please read our **[Contributing Guidelines](CONTRIBUTING.md)** to get started.

## 📜 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
