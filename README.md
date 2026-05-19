# learningAgent — Humpy dev home

**Humpy** is an AI agent aimed at both personal assistant and coding expert work. This repo is where we build it.

## Setup

Config under `.env/` at the repo root (parent of the `humpy` package). Paths come from [`humpy/hPath.py`](humpy/hPath.py) via `PKG_DIR = Path(__file__).resolve().parent` — same install location no matter what your cwd is.

| File | Purpose |
|------|---------|
| `.env/humpy.json` | `sdk`, `modelId`, `defaultBot` (gitignored; copy from example) |
| `.env/model.json` | API models array (gitignored) |
| `.env/humpy.example.json` | template |
| `.env/model.example.json` | template |

```bash
cd D:\git\learningAgent
copy .env\humpy.example.json .env\humpy.json
copy .env\model.example.json .env\model.json

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
  index.jsonl       # session catalog
  sessions/*.jsonl  # user / assistant turns only
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

Overrides: `LOCAL_MODEL_ID`, `HUMPY_SDK`, `HUMPY_BOT`, `CODEX_CWD`
