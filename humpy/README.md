# Humpy package

Core library for the Humpy CLI agent. Repo-level setup and run instructions live in the [root README](../README.md).

## Layout

Paths are anchored to the installed package (`PKG_DIR`), not the shell cwd. Repo root is `PKG_DIR.parent` (`.env/`, `.data/` sit next to this package).

```text
learningAgent/
  .env/              humpy.json, model.json
  .data/<bot>/       per-bot data (see bot.py)
  humpy/             this package
    memory/
      store.py       jsonl + index persistence
      pick.py        latest-N context selection for the model
```

## Modules

| Module | Role |
|--------|------|
| `hPath.py` | Resolve `PKG_DIR`, repo root, `.env` config files, and `.data/<bot>/` paths |
| `config.py` | Load `humpy.json` (global + per-bot settings) and `model.json` (API model rows) |
| `bot.py` | `Bot` — list/adopt bots, paths, developer prompt from config or `prompt.json` |
| `prompt.py` | Built-in developer and title prompts (fallback only) |
| `memory/store.py` | Session jsonl and bot `index.jsonl`; `turnCount` in index metadata |
| `memory/pick.py` | Build API-ready messages (latest `maxRecentTurns`, token cap estimate) |
| `message.py` | LLM completion (Anthropic or OpenAI) |
| `session.py` | `ChatSession` — one turn: pick → call → save on success |
| `cli.py` | Interactive CLI (`humpy` entry point) |

`__init__.py` is only a package marker. Import from the module that owns the behavior.

## Data flow (one turn)

```text
cli.py
  -> session.ChatSession.turn()
       -> store.loadSessionHistory
       -> pick.buildModelInput (developer + history + current user)
       -> message.complete
       on success (if saveSessions):
         -> store.appendTurn (user + assistant pair)
         -> store.updateSessionMeta (turnCount)
       on failure:
         -> no write (no orphan user line)
```

`turnCount` = completed assistant replies. Stored in `index.jsonl` per session; old sessions without it fall back to scanning jsonl once.

## Config (`humpy.json`)

Global fields: `defaultBot`, `maxRecentTurns`, `maxContextTokens`, `sessionTitleMaxChars`, `autoTitle`, `saveSessions`, `sessionMenuLimit`, `primaryBotShow`, `othersBotLimit`, `sdk`, `modelId`.

Per-bot under `bots.<name>` (merged with `bots.default`): `promptFile`, `model`, `temperature`, `maxOutputTokens`.

Config is loaded as-is from `.env/humpy.json` and `.env/model.json` (copy from `.env.example/`). API keys stay in `model.json` only.

## On disk (per bot)

```text
.data/<botName>/
  prompt.json           developer instructions (legacy / fallback)
  index.jsonl           session catalog (includes turnCount)
  sessions/<id>.jsonl   user / assistant turns
```

## Quick imports

```python
from humpy.session import ChatSession
from humpy.bot import Bot
from humpy.config import loadHumpyCfg, resolveBotSettings
from humpy.memory.pick import buildModelInput
from humpy.memory.store import loadIndexEntries
```

## Run

```bash
humpy
humpy --bot main --new
humpy --bot main --resume 20260518-120000
```

Slash commands (not saved to history, no LLM): `/help`, `/exit`, `/status`, `/sessions`, `/load <id>`, `/reset`, `/export <path>`, `/title <text>`. See [`commands.py`](commands.py).

Edit `.env/humpy.json` to change bots, limits, and defaults.
