# quick summary

Humpy is a small Python chat kernel. One user message → one llm reply, saved to jsonl.

Three steps, three modules: **bot** → **session** → **message**. `cli.py` runs the REPL. No tools, no agent loop yet.

---

# steps

## step 1 — pick a bot (`bot.py`)

module: `bot.py` — one named agent (sdk, model, prompt, limits)

1. list who exists — `bot.list()` / `bot.listName()`
2. adopt by name — `bot.adopt(name)` → `bot.ensure()`
3. first-time setup — `bot.ensure()` creates dirs; `bot._seedBotJson()` writes `.data/<bot>/bot.json` from `config.defaultBotProfile()`
4. read prompt/settings later — `bot.loadDeveloper()`, `bot.botCfg`

## step 2 — open a session (`session.py`)

module: `session.py` — one conversation thread + turn orchestration

1. new thread — `session.ChatSession(bot)` → new id, `store.registerSession()` in `index.jsonl`, empty `sessions/<id>.jsonl`
2. resume thread — `session.ChatSession(bot, sessionId=..., resume=True)` → load history, turn count
3. one exchange — `session.turn(userText)`:
   - `store.loadSessionHistory()`
   - `pick.buildModelInput()` — trim history
   - call **step 3** `message.complete()`
   - `store.appendTurn()` on success

cli: `cli.pickBot()` / `cli.pickSession()`, or `--bot`, `--new`, `--resume`. slash cmds in `commands.py`.

## step 3 — call the model (`message.py`)

module: `message.py` — single llm round-trip (text only)

1. route by sdk — `message.complete()` reads `bot.json` `sdk`
2. anthropic — `message._completeAnthropic()` → `messages.create`
3. openai — `message._completeOpenai()` → `chat.completions.create`
4. return — `{ text, usage }` back to `session.turn()`

model row from `config.loadModel()` + `.env/model.json`. sdk imported lazily on first call.

---

not built: agent loop (observation → second call), streaming, skills, benerd. tools: `humpy/tools/` + `playground/tool/test.py`
