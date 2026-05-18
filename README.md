# learningAgent

Config under `.env/`. Path resolution (`humpy/pathBoot.py`):

| How you run | What happens |
|-------------|----------------|
| **Terminal** `cd D:\git\learningAgent` | cwd has `.env/` → repo = cwd |
| **IDE / other cwd** | Walk parents for `.env/local.json` → use `repoPath` from JSON |

| File | Purpose |
|------|---------|
| `.env/model.json` | API models array (gitignored) |
| `.env/local.json` | `{ "repoPath": "D:\\git\\learningAgent" }` (gitignored) |
| `.env/model.example.json` | template |
| `.env/local.example.json` | template |

```bash
cd D:\git\learningAgent
copy .env\model.example.json .env\model.json
copy .env\local.example.json .env\local.json

pip install -r requirements.txt
python playground\helloworldApi.py
python playground\helloworldAgent.py
```

Overrides: `REPO_PATH`, `LOCAL_JSON` (full path to local.json), `MODEL_JSON`, `LOCAL_MODEL_ID`, `CODEX_CWD`
