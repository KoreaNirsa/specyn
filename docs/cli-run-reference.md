# CLI Run Reference

## `setup`

```bash
python specyn.py setup
```

What it does:

- creates or updates `.env`
- chooses `chatgpt` or `openapi` auth mode
- reuses or refreshes ChatGPT-linked login state
- accepts or updates `OPENAI_API_KEY`
- chooses the execution model
- validates Docker-backed agent readiness when Docker Desktop is available

## `auth-status`

```bash
python specyn.py auth-status
```

Shows:

- auth mode
- API key presence
- Docker readiness hints
- local Codex/auth cache hints

## `doctor`

```bash
python specyn.py doctor
```

Checks the local environment, including:

- Python
- Node.js and npm
- Docker CLI and daemon
- related local runtime readiness

## `up -d` / `down`

```bash
python specyn.py up -d
python specyn.py down
```

Starts and stops the dashboard stack.

## `sample-up -d` / `sample-down`

```bash
python specyn.py sample-up -d
python specyn.py sample-down
```

Starts and stops the sample-service stack.

## `validate`

```bash
python specyn.py validate --spec-dir specs/001-sample-service
```

## `compile-prompts`

```bash
python specyn.py compile-prompts --spec-dir specs/001-sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
```

## `run`

```bash
python specyn.py run --spec-dir specs/001-sample-service --project-id sample-service --workspace .workspace/sample-service
```

Generated output is written into local project/workspace paths, not meant to be blindly committed.

## Security Reminder

- `.env` is local-only
- `.specyn/codex` is local-only
- `.workspace/` is local-only
- check `.gitignore` before committing
