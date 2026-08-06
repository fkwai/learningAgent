# quick summary

Humpy chat kernel with a ReAct tool loop: one user message → model may call tools → observations → final text, saved to jsonl.

Core path: **bot** → **session** → **react** → **message** + **tools**. `cli.py` runs the REPL.

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
   - `react.run()` — tool loop (see step 3–4)
   - `store.appendTurn()` on success (final text only)

cli: `cli.pickBot()` / `cli.pickSession()`, or `--bot`, `--new`, `--resume`. slash cmds in `commands.py`.

## step 3 — call the model (`message.py`)

module: `message.py` — one llm round-trip (optional tools)

1. `message.complete(..., toolLst=...)` — openai or anthropic
2. returns `{ text, usage, toolCall }` (normalized)
3. `message.appendToolRound()` — splice assistant + tool observations into `message` for the next round

## step 4 — ReAct + tools (`react.py`, `tools/`)

module: `react.py` — loop until no `toolCall` or `maxAgentRound` (default 6)

1. `complete` with `humpy.tools.schema()`
2. for each call — `tools.run(name, arg, repoRoot=ROOT_DIR)`
3. `appendToolRound` → next `complete`
4. return final `{ text, usage, round }`

tools: `list_dir`, `read_file`, `shell` under `humpy/tools/`.

---

not built: tool traces in session jsonl, shell allowlists, streaming, skills, benerd.
