# Agent path: Codex CLI (ChatGPT login, no API key)
# setup: npm install -g @openai/codex  &&  codex login
# run:  cd D:\git\learningAgent
import subprocess

repo=r'D:\git\learningAgent'
userMsg='Reply with one short hello line only. Do not run commands or edit any files.'

proc=subprocess.run(
    [
        'codex','exec',
        '--sandbox','read-only',
        '--ask-for-approval','never',
        '--ephemeral',
        '--skip-git-repo-check',
        '-C',repo,
        userMsg,
    ],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace',
)
print(proc.stdout.strip())
