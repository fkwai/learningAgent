# Build Your Own Mini Claude Code from Scratch

The goal of Stage 1 is **not** to recreate the full Claude Code.

Instead, build the smallest working agent that includes:

- ReAct agent loop
- Shell tool
- Basic session management

---

# Core Components

## Prompt Engineering

Control a single LLM call by defining:

- Instructions
- Output format
- Few-shot examples
- Available tools
- Skill descriptions

---

## Session & Context

Manage multi-turn conversations through:

- Conversation history append
- Context assembly
- Context compression
- Few-shot injection

---

## CLI + Skills

Give the agent execution capabilities:

- Shell
- File operations
- CLI wrappers
- Reusable skills

---

# Learning Roadmap (7 Stages)

## Stage 1 — Basic Chat Loop

Implement a simple chat loop with conversation history.

**Goal**

- Message history
- Session append

---

## Stage 2 — System Prompt

Introduce persistent behavior.

**Includes**

- Role definition
- Behavioral boundaries
- Output format
- Long-term rules

---

## Stage 3 — ReAct Loop

Allow the model to reason before acting.

Typical flow:

```
Thought
↓
Action
↓
Observation
```

The observation is then fed back into the next reasoning step.

---

## Stage 4 — Tool Loop

Integrate external tools.

Tools include:

- Shell
- File operations
- Tool result injection

Typical workflow:

```
Thought
↓
Tool Call
↓
Observation
↓
Continue Reasoning
```

Examples:

- Shell tool (cwd, timeout, permissions)
- File tools (read, write, edit)
- Store observations into session

---

## Stage 5 — Context Compression

When history becomes too long:

- Summarize older messages
- Preserve the latest conversation verbatim

---

## Stage 6 — Skills

Package reusable procedures into skills.

Each skill can be dynamically injected into the context when needed.

---

## Stage 7 — Todo / Planning

Maintain task state across long-running jobs.

The agent should:

- Keep track of progress
- Remember unfinished work
- Avoid losing context

---

# Designing a Shell Tool

## Key Idea

An agent usually **does not invoke Bash directly**.

Instead, it interacts with an existing operating-system process runner.

Possible backends:

- Bash
- Zsh
- PowerShell
- CMD
- WSL

A shell tool is independent of the terminal UI, but depends on the execution environment:

- Working directory
- Environment variables
- PATH
- Permissions

If the host machine is isolated, commands should execute inside:

- Sandbox
- Container
- Remote runner

---

## What a Proper Shell Tool Should Support

A shell tool is **not** just a string executor.

It should behave like a controlled process runner.

Required features:

- Working directory (`cwd`)
- Timeout
- Environment variables
- Standard input (`stdin`)
- Standard output (`stdout`)
- Standard error (`stderr`)
- Exit code

It should also implement permission policies:

- Allowed commands
- Commands requiring confirmation
- Forbidden commands

Results should always be returned as structured data instead of raw terminal text.

---

# Shell Tool Architecture

## Shell Adapter

Chooses the appropriate shell:

- Bash
- Zsh
- PowerShell
- Custom runner

---

## Process Runner

Responsible for:

- Starting processes
- Streaming output
- Handling timeouts
- Interrupting execution

---

## Safety Policy

Responsible for:

- Command classification
- Permission checking
- Dangerous command blocking

---

## Result Formatter

Converts:

- stdout
- stderr
- exit code

into a structured result.

---

# Shell Tool API

## Input

```ts
type ShellToolInput = {
    command: string
    cwd?: string
    timeoutMs?: number
    env?: Record<string, string>
    stdin?: string
    reason?: string
}
```

## Output

```ts
type ShellToolResult = {
    exitCode: number | null
    stdout: string
    stderr: string
    durationMs: number
    truncated: boolean
    interrupted: boolean
}
```

---

# Stage 1 Deliverables

## CLI Chat

Supports:

- Multi-turn conversations
- System prompt
- Session history
- Basic exit commands

---

## Shell Tool

Supports:

- Command execution
- Structured results
- Permission control
- Timeouts
- Working directory
- Output truncation

---

## Agent Loop

The model should be able to:

1. Decide whether a tool is needed.
2. Invoke the tool.
3. Receive the observation.
4. Feed it back into the session.
5. Continue reasoning.

---

# Final Goal

Combining these three components gives you a minimal but fully functional AI agent that captures the core architecture behind Claude Code.

- CLI Chat
- Controlled Shell Tool
- ReAct Agent Loop

This forms the foundation upon which more advanced agent capabilities can be built.