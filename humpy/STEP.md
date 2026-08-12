# quick summary

Humpy is a CLI agent with sessions and a ReAct tool loop: one user message -> model may call tools -> tool results return to the model -> final answer. Conversation messages and tool traces are saved to the same session JSONL file.

Core path: **bot -> session -> pick -> react -> message + tools -> store**. `cli.py` runs the REPL.

---

# steps

## step 1 — pick a bot (`bot.py`)

Major entry: `Bot.adopt(name)`

1. `Bot.list()` / `Bot.listName()` lists existing bots.
2. `Bot.adopt(name)` creates a `Bot` and calls `Bot.ensure()`.
3. For a new bot, `Bot.ensure()` creates its directories and copies `defaultBotProfile` into `.data/<bot>/bot.json`.
4. The bot supplies the model, SDK, developer prompt, context limits, and agent-round limit used by later steps.

## step 2 — open a session (`session.py`)

Major entry: `ChatSession(bot, sessionId=None, resume=False)`

1. A new session gets an ID, a row in `.data/<bot>/index.jsonl`, and a JSONL file under `.data/<bot>/sessions/`.
2. A resumed session loads its metadata and finds the highest saved turn number.
3. `ChatSession.turn(userText)` controls one complete user turn.
4. Slash commands such as `/sessions`, `/load`, `/reset`, and `/export` are handled by `commands.py` without calling the model.

## step 3 — build the model input (`memory/pick.py`)

Major entry: `pick.buildModelInput(...)`

1. `store.loadSessionHistory()` loads only developer, user, and assistant conversation rows.
2. Trace rows with `entryType` are ignored, so old tool output is not automatically sent back to the model.
3. History is grouped into complete user/assistant turn pairs.
4. The latest pairs are kept according to `maxRecentTurns` and the approximate `maxContextTokens` budget.
5. The current user message is appended after the selected history.

This is context trimming, not context summarization. An unmatched user row from a failed turn remains on disk but is not included in later model input.

## step 4 — run the model and tools (`react.py`)

Major entry: `react.run(...)`

1. `message.complete()` calls the configured OpenAI or Anthropic endpoint with the prompt and tool schemas.
2. `message.py` normalizes the provider response into `text`, `usage`, and `toolCall`.
3. `react.run()` emits an `agent_round` trace event for that model response.
4. If there are no tool calls, the loop returns with `stopReason='completed'`.
5. Otherwise, each call is executed through `tools.run(name, arguments, repoRoot=...)`.
6. Each execution emits a `tool_result` trace event containing the call ID, tool name, arguments, structured result, and observation sent to the model.
7. `message.appendToolRound()` adds the assistant tool call and observations in the correct provider format.
8. The model is called again until it returns a final answer or reaches `maxAgentRound`.

Current tools: `list_dir`, `read_file`, and `shell` under `humpy/tools/`.

## step 5 — save the turn and trace (`session.py`, `memory/store.py`)

Major entry: `ChatSession.turn(userText)`

1. Before the model call, `store.appendUser()` saves the user row. This preserves the attempted turn if execution later fails.
2. During the ReAct loop, `store.appendTraceEvent()` immediately saves every `agent_round` and `tool_result`.
3. On success, `store.appendAssistant()` saves the final answer.
4. A final `turn_end` event records the overall status and number of rounds.
5. If the model loop raises an exception, `turn_end` is saved with `status='model_error'`.
6. If the round limit is reached, it is saved with `status='max_round_exceeded'`.

The session file therefore looks like:

```text
user
agent_round
tool_result
agent_round
assistant
turn_end
```

`toolCallId` connects a `tool_result` to the call recorded in `agent_round`. A failed tool does not automatically fail the turn because the model can inspect the error and recover in another round.

---

Not built yet: shell approvals and sandbox rules, repository path enforcement, trace redaction, streaming and cancellation, context summarization, skills, todo/planning state, trace display commands, and Benerd delegation.
