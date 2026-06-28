# Getting Started

## Prerequisites

- **Python 3.13+** (specified in `pyproject.toml`)
- **Google Chrome** installed (the browser the agent controls)
- **OpenRouter API key** ([get one here](https://openrouter.ai/))

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/crawl-engine.git
cd crawl-engine
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -e .
```

This installs the package in development mode along with all dependencies listed in `pyproject.toml`:
- `langchain` / `langchain-openai` — LLM integration
- `langgraph` — Agent orchestration framework
- `seleniumbase` / `undetected-chromedriver` — Browser automation
- `beautifulsoup4` — HTML parsing
- `deepagents` — Middleware for agent tooling
- `rich` — Colored console logging
- `python-dotenv` — Environment variable loading

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your OpenRouter API key:

```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
LLM_MODEL=deepseek/deepseek-v3.2
VISION_MODEL=qwen/qwen2.5-vl-32b-instruct
SUMMARIZATION_LLM=google/gemma-3-12b-it
```

---

## Running the Agent

```bash
python src/main.py
```

When you run `main.py`:

1. The `.env` file is loaded.
2. The OpenRouter API key is validated.
3. The LangGraph workflow is compiled.
4. A Chrome browser window opens (driven by `undetected-chromedriver`).
5. The agent begins executing its hardcoded mission (currently set to create a Discord account).
6. Streamed output appears in the terminal — the agent's thoughts (🧠) and actions (⚡) are displayed in real-time.
7. Press **Ctrl+C** to stop, or wait for the agent to finish. Press **Enter** to close the browser.

### Customizing the Goal

Edit `src/main.py` and change the `user_goal` variable:

```python
user_goal = "Create an account on discord. use ademhosni400@icloud.com as an email"
```

Replace this with any natural-language browsing task.

---

## LangGraph Platform (Optional)

The repository includes `langgraph.json` for deployment on the LangGraph Platform:

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/main.py:graph"
  }
}
```

This registers the compiled graph as an API endpoint. See [LangGraph documentation](https://langchain-ai.github.io/langgraph/) for deployment instructions.

---

## Troubleshooting

### Chrome Binary Not Found

If you see an error about the Chrome binary, update the path in `src/execution/browser.py:27`:

```python
binary_location=r"C:\Program Files (x86)\chrome\chrome.exe",
```

### OpenRouter API Key Invalid

Ensure your key starts with `sk-or-v1-` and has credits on your OpenRouter dashboard.

### Selenium Timeouts

Some pages load slowly. The `WebDriverWait` timeout is set to 1 second by default in the browser manager. Increase it if needed in `src/execution/browser.py:28`:

```python
self.wait = WebDriverWait(self.driver, 5)
```
