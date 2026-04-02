# Operations

## Recommended Run Order

```text
setup
  -> auth-status
  -> doctor
  -> up -d
  -> sample-up -d
```

## Required Local Tools

These should be installed on the machine before first use:

- Docker Desktop
- Python 3.11+
- Node.js 20+ and npm

Basic checks:

```bash
python --version
node --version
npm --version
docker version
```

## Core Commands

| Command | Purpose |
|---|---|
| `python specyn.py setup` | Create/update `.env`, choose auth mode, choose model, validate Docker agent when available |
| `python specyn.py auth-status` | Show auth mode, Docker readiness, and local auth/cache hints |
| `python specyn.py doctor` | Check local toolchain and Docker-related readiness |
| `python specyn.py up -d` | Start dashboard frontend/backend/AI server |
| `python specyn.py down` | Stop dashboard stack |
| `python specyn.py sample-up -d` | Start sample-service stack |
| `python specyn.py sample-down` | Stop sample-service stack |
| `python specyn.py validate ...` | Validate the spec bundle |
| `python specyn.py compile-prompts ...` | Compile prompts into `.specyn/prompts/...` |
| `python specyn.py run ...` | Execute the local SDD flow |

## Auth Modes

### `chatgpt`

- Uses local ChatGPT-linked Codex login cache
- Cache lives under `.specyn/codex`
- Docker Desktop should be running if you want the Docker agent to reuse that login immediately

### `openapi`

- Uses `OPENAI_API_KEY` from `.env`
- Treat `.env` as sensitive
- Never commit or share it

## Local-Only Files

These are local runtime artifacts and should not be committed:

- `.env`
- `.env.*`
- `.specyn/`
- `.workspace/`
- `node_modules/`
- local logs and caches

## Security Guidance

- Keep `.env` out of version control
- Keep `.specyn/codex` out of version control
- Review terminal output before sharing logs externally
- Be careful with screen recordings and screenshots during setup
- If using `openapi`, rotate the API key if you think it was exposed

## UI Notes

- The Dashboard page is now status-oriented
- Agent execution lives in the Workspace page
- Live conversation is filtered to agent messages, while raw step logs are hidden behind details panels

## Common Ports

| Service | Port | URL |
|---|---|---|
| Dashboard Frontend | `4173` | `http://localhost:4173` |
| Dashboard Backend | `8180` | `http://localhost:8180/api/v1/spec-runs/health` |
| Dashboard AI Server | `8100` | `http://localhost:8100/health` |
| sample-service Frontend | `5173` | `http://localhost:5173` |
| sample-service Backend | `8080` | `http://localhost:8080/api/v1/generated/sample-service/summary` |
| sample-service AI Server | `8000` | `http://localhost:8000/generated/sample-service/context` |
