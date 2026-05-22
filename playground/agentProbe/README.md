# agentProbe — one-round first-step probes

Two tiny scripts, each sending **exactly one** model call for the same task. Tools are declared but **never executed**. Goal: see what the model asks for on the first agent step when the request is shaped like Codex vs XiaoBa.

## Task (hardcoded in both scripts)

```
repoRoot = D:/git/learningAgent
userTask = Read this repo and figure out what it is doing. Start by inspecting the project structure.
```

## What “Codex-like” means here

Mimics **OpenAI Responses API** first sampling (`ResponsesApiRequest`), not the full `run_turn` loop:

| Piece | Real Codex source | This probe |
|-------|-------------------|------------|
| Instructions | `client.rs` → `build_responses_request` uses `prompt.base_instructions.text` | Short Codex-style CLI agent stub |
| Input | `protocol/models.rs` → `ResponseInputItem::Message` with `input_text` | `[{type:message, role:user, content:[{type:input_text,...}]}]` |
| Tools | `tools/src/tool_spec.rs` → `{type:function, name, description, strict, parameters}` | `list_dir`, `read_file`, `grep` (probe stand-ins; real Codex often exposes `shell_command` / `apply_patch`) |
| Flags | `tool_choice: auto`, `parallel_tool_calls: false` | Same |

Saved file: `out/codexOneRoundRequest.json` is the **canonical Codex wire shape**. The HTTP call may translate to Anthropic/OpenAI **chat + tools** if your model config does not expose `/v1/responses` (see `_note` in the JSON).

## What “XiaoBa-like” means here

Mimics **first turn of `ConversationRunner`** via `OpenAIProvider.buildRequestBody`:

| Piece | Real XiaoBa source | This probe |
|-------|-------------------|------------|
| System | `prompts/system-prompt.md` + `PromptManager` / workspace injection | Abbreviated Chinese system prompt + `当前工作目录` |
| Messages | `messages[]` with `system` then `user` | Same |
| Tools | `ToolDefinition` → `{type:function, function:{name, description, parameters}}` | `list_dir`, `read_file` (XiaoBa uses `file_path`), `grep` |
| No loop | `conversation-runner.ts` `run()` would loop on `toolCalls` | Single call only |

Saved file: `out/xiaobaOneRoundRequest.json`.

## Source references (repos in workspace, not imported)

**Codex** (`d:\git\codex-main\codex-rs`):

- `core/src/session/turn.rs` — `build_prompt`, `run_sampling_request`
- `core/src/client.rs` — `build_responses_request`
- `codex-api/src/common.rs` — `ResponsesApiRequest`
- `core/src/client_common.rs` — `Prompt`
- `tools/src/tool_spec.rs` — `create_tools_json_for_responses_api`
- `tools/src/responses_api.rs` — `ResponsesApiTool`
- `protocol/src/models.rs` — `ResponseInputItem`, `ContentItem`

**XiaoBa-CLI** (`d:\git\XiaoBa-CLI-main`):

- `src/core/conversation-runner.ts` — `ConversationRunner.run`
- `src/providers/openai-provider.ts` — `buildRequestBody`
- `src/utils/prompt-manager.ts` — `buildSystemPrompt`
- `prompts/system-prompt.md`, `prompts/behavior.md`
- `src/tools/read-tool.ts`, `grep-tool.ts`, `glob-tool.ts`

## Config

Both scripts load API keys from **humpy** (`.env/model.json`, `.env/humpy.json`). Edit `MODEL_ID` at the top of each script if needed (default: `minimax-m27-highspeed`).

Requires: `anthropic` and/or `openai` Python package (same as humpy).

## Run

From repo root:

```bash
python playground/agentProbe/probeCodexOneRound.py
python playground/agentProbe/probeXiaoBaOneRound.py
```

Outputs:

- `playground/agentProbe/out/codexOneRoundRequest.json`
- `playground/agentProbe/out/codexOneRoundResponse.json`
- `playground/agentProbe/out/xiaobaOneRoundRequest.json`
- `playground/agentProbe/out/xiaobaOneRoundResponse.json`

Console sections: `REQUEST PAYLOAD`, `RAW MODEL RESPONSE`, `PARSED ACTION IF POSSIBLE`.

## What to compare in the first response

1. **Tool vs text** — Does the model call `list_dir` / `read_file` / `grep` immediately, or answer from priors?
2. **Which tool first** — Codex-shaped instructions often push “explore”; XiaoBa system text emphasizes 先理解再行动.
3. **Preamble** — XiaoBa commonly allows `content` + `tool_calls` in one assistant message; check for text before tools in the raw JSON.
4. **Argument shape** — Codex probe uses `path`; XiaoBa `read_file` uses `file_path` (matches real XiaoBa schema).
5. **Parallel calls** — Multiple `tool_calls` in one round vs one at a time.

Neither script runs tools — if you see `tool_calls` / `tool_uses`, that is the model’s requested first action.
