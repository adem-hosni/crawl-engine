# Logger

**File:** `src/config/logger.py`

Configures dual-output logging: human-friendly colored console output via [Rich](https://rich.readthedocs.io/) and detailed rotating file logs for debugging.

---

## Configuration

### Console Handler (Rich)

```python
"console": {
    "class": "rich.logging.RichHandler",
    "level": "INFO",
    "formatter": "rich_format",
    "rich_tracebacks": True,
    "markup": True,
    "show_path": False,
}
```

- Outputs **INFO** and above to the console.
- Rich tracebacks for exception stack traces.
- Markup support for colored/bold text.
- No module path shown (cleaner output).

### File Handler (RotatingFileHandler)

```python
"file": {
    "class": "logging.handlers.RotatingFileHandler",
    "level": "DEBUG",
    "formatter": "file_format",
    "filename": "logs/agent.log",
    "maxBytes": 10 * 1024 * 1024,   # 10 MB per file
    "backupCount": 5,                # Keep 5 rotated files
    "encoding": "utf-8",
}
```

- Captures **DEBUG** and above to file (more verbose than console).
- Rotates at 10 MB, keeping up to 5 backup files.
- UTF-8 encoding for international characters.

---

## Log Level Configuration

| Logger | Console Level | File Level |
|---|---|---|
| `root` | INFO | INFO |
| `src` | DEBUG | DEBUG |
| `selenium` | — | WARNING |
| `urllib3` | — | WARNING |
| `httpx` | — | WARNING |
| `webdriver_manager` | — | WARNING |

External library loggers (`selenium`, `urllib3`, `httpx`, `webdriver_manager`) are set to **WARNING** to avoid noise from their internal debug/info logs.

---

## `get_logger(name)`

The recommended way to obtain a logger in any module:

```python
from config.logger import get_logger
logger = get_logger("my.module")
```

This ensures:
1. The logging config is applied (via `dictConfig`).
2. All loggers follow the above hierarchy.
3. Log calls appear in both console and file output.

### Usage Across the Codebase

```python
# src/execution/browser.py
logger = get_logger("execution.browser")
logger.info(f"Navigating to {url}")
logger.error(f"Navigation error: {e}")

# src/planning/strategist.py
logger = get_logger("planning.strategist")
logger.info(response.content.strip())

# src/graph/nodes.py
logger = get_logger("core.callbacks")
logger.info(f"Summarization triggered on {len} chars...")
```

---

## Log Output Examples

### Console (via Rich)

```
[14:32:01] INFO     --- 🚀 DEEP AGENT SAAS: STARTING ---
[14:32:02] INFO     Graph built successfully.
[14:32:03] INFO     👀 PERCEPTION: Scanned https://discord.com/register
[14:32:05] INFO     ⚡ ACTION: Using 'click_element' with args: {'element_id': 3}
[14:32:06] INFO     🛠️ TOOL OUTPUT: Action on [3]: Clicked (Standard)
```

### File (logs/agent.log)

```
[INFO] main: --- 🚀 DEEP AGENT SAAS: STARTING ---
[INFO] planning.strategist: I need to navigate to Discord's registration page...
[DEBUG] execution.browser: Navigation error: ...
```

---

## Log Directory

Logs are stored in `logs/agent.log` (relative to the project root). The directory is created automatically on first import:

```python
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
```
