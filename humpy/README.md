# Humpy package

Core library for the Humpy CLI agent. Repo-level setup and run instructions live in the [root README](../README.md).

## Layout

Paths are anchored to the installed package (`PKG_DIR`), not the shell cwd. Repo root is `PKG_DIR.parent` (`.env/`, `.data/` sit next to this package).

```text
learningAgent/
  .env/              humpy.json, model.json
  .data/<bot>/       per-bot data (see bot.py)
  humpy/             this package
```

## Modules

| Module | Role |
|--------|------|
| `hPath.py` | Resolve `PKG_DIR`, repo root, `.env` config files, and `.data/<bot>/` paths |
| `config.py` | Load `humpy.json` (sdk, default model, default bot) and `model.json` (API model rows) |
| `bot.py` | `Bot` — list/adopt bots, paths, `prompt.json` / developer prompt |
| `prompt.py` | Built-in developer and title prompts |
| `memory.py` | Session JSONL and bot `index.jsonl` (append, load, register, headlines) |
| `message.py` | One-shot LLM completion (Anthropic or OpenAI) from a model config row |
| `session.py` | `ChatSession` — ties bot, config, memory, and message into a chat turn loop |
| `cli.py` | Interactive CLI (`humpy` entry point) |

`__init__.py` is only a package marker. Import from the module that owns the behavior, e.g. `from humpy.session import ChatSession`.

## Data flow (one turn)

```text
cli.py
  -> session.ChatSession.turn()
       -> memory.appendUser / loadMessages
       -> bot.loadDeveloper() (or prompt.DEV_PROMPT_DEFAULT)
       -> message.complete (config.loadModel + humpy sdk)
       -> memory.appendAssistant
       -> optional title via message.complete + memory.updateIndexHeadline
```

## On disk (per bot)

```text
.data/<botName>/
  prompt.json           developer instructions
  index.jsonl           session catalog
  sessions/<id>.jsonl   user / assistant turns
```

## Quick imports

```python
from humpy.session import ChatSession
from humpy.bot import Bot
from humpy.config import loadHumpyCfg, loadModel

bot=Bot.adopt('main')
bot.loadDeveloper()
bot.indexFile
```

## Run

```bash
humpy
humpy --bot main --new
humpy --bot main --resume 20260518-120000
```

Optional env overrides: `HUMPY_SDK`, `LOCAL_MODEL_ID`, `HUMPY_BOT` (see `config.py`).
