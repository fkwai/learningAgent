# agentProbe — one-round first-step probes

Compare **Codex-shaped** vs **XiaoBa-shaped** first model calls for the same task. Tools are declared but **never executed**.

## Layout

```
playground/agentProbe/
  _lib/              shared: paths, task, model loader (reads humpy .env), http_call, parse, probe_io
  codex/
    tools.py         Responses API tool definitions (flat name + parameters)
    prompt.py        instructions + input items → request.json shape
    call.py          one HTTP round (flat tool schema)
    runOneRound.py   entry script
  xiaoba/
    tools.py         OpenAI chat tool definitions (nested function key)
    prompt.py        system + user messages → request.json shape
    call.py          one HTTP round (nested tool schema)
    runOneRound.py   entry script
  out/
    codex/request.json, response.json
    xiaoba/request.json, response.json
```

**Path bootstrap:** All directory constants live in `_lib/paths.py` (hardcoded `ROOT`, derived probe paths). Entry scripts only hardcode one line — the path to that file — then load it with `importlib`:

```python
PATHS_PY=r'D:/git/learningAgent/playground/agentProbe/_lib/paths.py'
# ... importlib load + paths.setup_sys_path('codex'|'xiaoba')
```

Must match `PATHS_PY` inside `paths.py`. Everything else (`LIB_PROBE`, `CODEX_PROBE`, `OUT_*`, …) comes from there.

Config keys still come from **humpy** (`.env/model.json`) via `_lib/model.py` — no probe code lives under `humpy/`.

## Task (both probes)

```
repoRoot = D:/git/learningAgent
userTask = Read this repo and figure out what it is doing. Start by inspecting the project structure.
```

Edit `DEFAULT_MODEL_ID` in `_lib/task.py` if needed.

## Run

From repo root:

```bash
python playground/agentProbe/codex/runOneRound.py
python playground/agentProbe/xiaoba/runOneRound.py
```

## What each folder mimics

| | **codex/** | **xiaoba/** |
|---|------------|-------------|
| Wire shape | Responses API: `instructions`, `input[]`, tools with top-level `name` | Chat: `messages[]`, tools with `function.{name,description,parameters}` |
| read_file arg | `path` | `file_path` |
| Saved request | Canonical Codex JSON | Canonical XiaoBa JSON |
| HTTP | `_lib/call.py` adapts to OpenAI chat or Anthropic messages per model `sdk` | same |

## Compare in the first response

1. Tool vs text on step one  
2. Which tool is called first (`list_dir` vs `read_file` vs `grep`)  
3. Text preamble before tools (common in XiaoBa)  
4. Argument names (`path` vs `file_path`)  
5. Multiple `tool_calls` in one round vs one

## Source references (not imported)

- Codex: `codex-rs/core/src/client.rs`, `tools/src/tool_spec.rs`, `protocol/src/models.rs`
- XiaoBa: `src/core/conversation-runner.ts`, `src/providers/openai-provider.ts`, `src/types/tool.ts`
