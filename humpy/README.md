# Humpy package

Core library for the Humpy CLI agent. Repo-level setup and run instructions live in the [root README](../README.md).

## Layout

Paths are anchored to the installed package (`PKG_DIR`), not the shell cwd. Repo root is `PKG_DIR.parent` (`.env/`, `.data/` sit next to this package).

```text
learningAgent/
  .env/              humpy.json (agent), model.json (API keys)
  .env.example/      templates without secrets
  .data/<bot>/       bot.json, index.jsonl, sessions/
  humpy/             this package
    memory/
      store.py       jsonl + index persistence
      pick.py        latest-N context selection for the model
```

## Config

| File | Scope |
|------|--------|
| `.env/humpy.json` | Agent: `defaultBot`, menu limits (`primaryBotShow`, `othersBotLimit`, …), `defaultBotProfile` template for new bots |
| `.data/<bot>/bot.json` | Bot: `sdk`, `model`, `temperature`, `maxOutputTokens`, memory limits, `developer`, `saveSessions`, title settings |
| `.env/model.json` | API model rows (keys, baseUrl) |

New bots: `Bot.ensure()` writes `bot.json` from `defaultBotProfile`. If legacy `prompt.json` exists, its `developer` field is copied into `bot.json` once.

## Modules

| Module | Role |
|--------|------|
| `hPath.py` | Paths for `.env`, `.data/<bot>/` |
| `config.py` | `loadAgentCfg()`, `loadBotCfg()`, `loadModel()` |
| `bot.py` | `Bot` — list/adopt, seed/load `bot.json` |
| `prompt.py` | Built-in fallbacks only (`DEV_PROMPT_DEFAULT`, `TITLE_PROMPT`) |
| `memory/store.py` | Session jsonl and index; `turnCount` |
| `memory/pick.py` | API-ready messages from `bot.json` limits |
| `message.py` | LLM call (lazy-imports one SDK per `bot.json` `sdk`) |
| `session.py` | `ChatSession` — pick → call → save on success |
| `commands.py` | Slash commands (no LLM) |
| `cli.py` | Interactive CLI |

## Startup

`humpy` avoids importing `anthropic` / `openai` until the first model call. `ChatSession` is imported only when a chat session starts.

## Data flow (one turn)

```text
cli → session.turn()
  → store.loadSessionHistory
  → pick.buildModelInput (botCfg)
  → message.complete (lazy SDK import)
  on success → store.appendTurn, update turnCount
```

## On disk (per bot)

```text
.data/<botName>/
  bot.json              bot settings + developer prompt
  index.jsonl           session catalog (turnCount)
  sessions/<id>.jsonl   turns
```

## Quick imports

```python
from humpy.session import ChatSession
from humpy.bot import Bot
from humpy.config import loadAgentCfg, loadBotCfg
```

## Run

```bash
humpy
humpy --bot main --new
```

Slash commands: `/help`, `/exit`, `/status`, `/sessions`, `/load`, `/reset`, `/export`, `/title`.
