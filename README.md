# learningAgent — Humpy dev home

**Humpy** is an AI agent aimed at both personal assistant and coding expert work. This repo is where we build it.

## Setup

Config under `.env/` at the repo root (parent of the `humpy` package). Paths come from [`humpy/hPath.py`](humpy/hPath.py) via `PKG_DIR = Path(__file__).resolve().parent` — same install location no matter what your cwd is.

| File | Purpose |
|------|---------|
| `.env/humpy.json` | global + per-bot settings (gitignored; copy from example) |
| `.env/model.json` | API models + keys (gitignored) |
| `.env.example/humpy.json` | template (no secrets) |
| `.env.example/model.json` | template (`apiKey` placeholder) |

```bash
cd D:\git\learningAgent
mkdir .env 2>nul
copy .env.example\humpy.json .env\humpy.json
copy .env.example\model.json .env\model.json
# edit .env\model.json and set your real apiKey

python -m pip install -e .
```

## Run Humpy

```bash
humpy                    # pick bot, new or resume session, chat
humpy --bot main --new
humpy --bot main --resume 20260518-120000
```

`humpy.json` **sdk**: `anthropic` or `openai` (same model row in `model.json`, different baseUrl key).

## Bots and memory

Each **bot** is a folder under `.data/<botName>/`:

```text
.data/main/
  prompt.json       # {"developer": "..."} — instructions for this bot
  index.jsonl       # session catalog (turnCount per session)
  sessions/*.jsonl  # user / assistant turns (saved after successful model reply)
```

On first use, `prompt.json` is created from the default in [`humpy/prompt.py`](humpy/prompt.py). Package layout: [`humpy/README.md`](humpy/README.md).

**Migration:** if you have old `.data/chatloop/`, move it to `.data/main/` (sessions + index.jsonl) and add `prompt.json`.

Regression (real API):

```bash
python app/regressWorkoutWeek.py
```

Playground (optional):

```bash
python playground\hw\hwApiAnthropic.py
python playground\hw\hwApiCodex.py
python playground\hw\hwAgent.py
python playground\chatloop\chatLoop.py
```

All runtime settings come from `.env/humpy.json` and `.env/model.json` (no env-var overrides).
