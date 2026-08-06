# learningAgent — Humpy (and later Benerd)

This repo is an **office**: two agents that work together, like *Yes Minister*.

| | **Humpy** | **Benerd** |
|--|-----------|------------|
| Role | Think, decide, instruct | Do long, boring, many-iteration work |
| Model | Big LLM via API | Small LLM on local GPU |
| Examples | Plan, review, talk to you, delegate | Hunt memory, summarize huge texts, draft tools |

**Right now we only build Humpy.** Benerd is a placeholder (`benerd/`); shared “office” packaging can wait until Humpy’s tool loop is solid. Tools live under **`humpy/tools/`** for now.

Learning roadmap for the agent loop: [`tutorial.md`](tutorial.md). Package detail: [`humpy/README.md`](humpy/README.md).

---

## Setup

Config under `.env/` at the repo root. Paths come from [`humpy/hPath.py`](humpy/hPath.py) via `PKG_DIR` — same install location no matter what your cwd is.

| File | Purpose |
|------|---------|
| `.env/humpy.json` | Agent settings + **`defaultBotProfile`** (template for new bots; gitignored) |
| `.env/model.json` | API models + keys (gitignored) |
| `.env.example/humpy.json` | Copy template only — **not read at runtime** |
| `.env.example/model.json` | Copy template only (`apiKey` placeholder) |

```bash
cd D:\git\learningAgent
mkdir .env 2>nul
copy .env.example\humpy.json .env\humpy.json
copy .env.example\model.json .env\model.json
# edit .env\model.json — set your real apiKey
# optional: edit defaultBotProfile inside .env\humpy.json

python -m pip install -e .
```

**Runtime reads only `.env/` and `.data/`** — never `.env.example/`.

On first use of a bot, `Bot.ensure()` copies `defaultBotProfile` from `.env/humpy.json` into `.data/<name>/bot.json`. Legacy `prompt.json` `developer` is merged in once if present.

## Run Humpy

```bash
humpy
humpy --bot main --new
humpy --bot main --resume 2605181200-a3f2
```

Bot `sdk` in `bot.json`: `anthropic` or `openai` (matching `baseUrl` in `model.json`).

## Bots and memory

```text
.data/main/
  bot.json          sdk, model, limits, developer prompt
  index.jsonl       session catalog (headline, metadata)
  sessions/*.jsonl  turns (saved after successful reply)
```

## Tools (Humpy for now)

```text
humpy/tools/
  __init__.py     schema() + run(name, arg)
  listDir.py
  readFile.py
  shell.py        CLI wrapper — command / cwd / timeout_ms
```

Playground probe (LLM calls tool → execute):

```bash
python playground/tool/test.py
```

## More

```bash
python app/regressWorkoutWeek.py
python playground/chatloop/chatLoop.py
```
