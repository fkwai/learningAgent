# learningAgent — Humpy dev home

**Humpy** is an AI agent aimed at both personal assistant and coding expert work. This repo is where we build it.

## Setup

Config under `.env/` at the repo root. Paths come from [`humpy/hPath.py`](humpy/hPath.py) via `PKG_DIR` — same install location no matter what your cwd is.

| File | Purpose |
|------|---------|
| `.env/humpy.json` | Agent settings + `defaultBotProfile` template (gitignored) |
| `.env/model.json` | API models + keys (gitignored) |
| `.env.example/humpy.json` | Agent template |
| `.env.example/model.json` | Model template (`apiKey` placeholder) |
| `.env.example/bot.json` | Per-bot template (copy into `.data/<bot>/bot.json` if needed) |

```bash
cd D:\git\learningAgent
mkdir .env 2>nul
copy .env.example\humpy.json .env\humpy.json
copy .env.example\model.json .env\model.json
# edit .env\model.json — set your real apiKey

python -m pip install -e .
```

Each bot under `.data/<name>/` has its own `bot.json` (created on first use from `defaultBotProfile`). Legacy `prompt.json` is migrated into `bot.json` automatically.

## Run Humpy

```bash
humpy
humpy --bot main --new
humpy --bot main --resume 20260518-120000
```

Bot `sdk` in `bot.json`: `anthropic` or `openai` (matching `baseUrl` in `model.json`).

## Bots and memory

```text
.data/main/
  bot.json          sdk, model, limits, developer prompt
  index.jsonl       session catalog (turnCount)
  sessions/*.jsonl  turns (saved after successful reply)
```

Package layout: [`humpy/README.md`](humpy/README.md).

Regression (real API):

```bash
python app/regressWorkoutWeek.py
```

Playground (optional):

```bash
python playground\hw\hwApiAnthropic.py
python playground\chatloop\chatLoop.py
```
