# Humpy package

Core library for the Humpy CLI agent. Repo-level setup and run instructions live in the [root README](../README.md).

## Layout

Paths are anchored to the installed package (`PKG_DIR`), not the shell cwd. Repo root is `PKG_DIR.parent` (`.env/`, `.data/` sit next to this package).

```text
learningAgent/
  .env/              humpy.json (agent + defaultBotProfile), model.json
  .env.example/      copy templates only (not loaded by code)
  .data/<bot>/       bot.json (per-bot copy), index.jsonl, sessions/
  humpy/             this package
    memory/
      store.py       jsonl + index persistence
      pick.py        latest-N context selection for the model
```

## Config

| File | Scope |
|------|--------|
| `.env/humpy.json` | Agent: `defaultBot`, menu limits, **`defaultBotProfile`** (bot defaults for new bots) |
| `.data/<bot>/bot.json` | Per-bot runtime config (copy of profile at create time; editable per bot) |
| `.env/model.json` | API model rows (keys, baseUrl) |

There is **no** `bot.json` under `.env/`. The default bot shape lives only as `defaultBotProfile` inside `humpy.json`. `Bot.ensure()` writes `.data/<name>/bot.json` from that object (plus legacy `prompt.json` `developer` if present).

## Modules

| Module | Role |
|--------|------|
| `hPath.py` | Paths for `.env`, `.data/<bot>/` |
| `config.py` | `loadAgentCfg()`, `loadBotCfg()`, `loadModel()` |
| `bot.py` | `Bot` — list/adopt, seed/load `bot.json` |
| `utils.py` | Shared helpers (`fmtTs`, `newSessionId`) |
| `prompt.py` | Built-in fallbacks (`DEV_PROMPT_DEFAULT`) |
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
  on success → store.appendTurn (turn count lives in session jsonl)
```

## Session ids

New sessions use `YYMMDDHHMM-hex4` UTC (e.g. `2605260356-744f`). Optional prefix: `regress-2605260356-d842`. Older `YYYYMMDD-HHMMSS` ids still resume normally.

## On disk (per bot)

```text
.data/<botName>/
  bot.json              bot settings + developer prompt
  index.jsonl           session catalog (headline, paths; turns from session file)
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
