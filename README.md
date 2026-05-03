# Specyn
<img width="100%" height="600" alt="specyn-logo" src="https://github.com/user-attachments/assets/1cb4ea88-b113-4cf0-8592-d88c73db9830" />

Specyn is a Spec Driven Development workspace that connects spec bundles, agent execution, generated code, runtime verification, and a dashboard UI.

The default operating model is:

1. Configure local auth and runtime settings with `python specyn.py setup`
2. Start the dashboard stack with Docker
3. Run agents from the Workspace page
4. Review generated results in `projects/sample-service` and `.workspace`

Spec locations:

- `specs/templates/` for new bundle templates
- `specs/001-sample-service/` for the reference sample bundle used by `validate`, `compile-prompts`, and `run`

## Prerequisites

You should install and verify these before the first run:

- Docker Desktop
- Python 3.11+ with `python` available in PATH
- Node.js 20+ and npm

Recommended checks:

```bash
python --version
node --version
npm --version
docker version
```

Important:

- Docker Desktop should be installed before the first full run.
- `setup` can still write `.env` even if Docker Desktop is not started yet.
- ChatGPT auth reuse and Docker agent validation require Docker Desktop to be running.

## First-Time Setup

Run from the repository root:

```bash
python specyn.py setup
python specyn.py auth-status
python specyn.py doctor
python specyn.py up -d
```

Dashboard URLs:

- Frontend: `http://localhost:4173`
- Backend: `http://localhost:8180`
- AI Server: `http://localhost:8100`

If you also want to run the generated sample runtime:

```bash
python specyn.py sample-up -d
```

Sample-service URLs:

- Frontend: `http://localhost:5173`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- AI Server context: `http://localhost:8000/generated/sample-service/context`

Stop commands:

```bash
python specyn.py down
python specyn.py sample-down
```

## What `setup` Does

`python specyn.py setup` manages:

- `.env` creation or update
- auth mode selection: `chatgpt` or `openapi`
- ChatGPT login reuse or relogin
- OpenAI API key input or update
- model selection
- Docker agent validation when Docker Desktop is available

## Security Notes

Initial users should be careful about local auth artifacts.

- Do not commit `.env`
- Do not share `.specyn/codex` because it can contain local auth cache
- Do not paste full logs publicly if they may include paths, prompts, request payloads, or local runtime information
- Treat `OPENAI_API_KEY` as a secret
- Treat workspace outputs in `.workspace/` as local-only run artifacts unless explicitly reviewed
- If you use screen sharing, avoid exposing `.env`, terminal history, or Docker logs that may contain sensitive values

## Key Local Paths

- `.env`: local runtime settings
- `.specyn/codex`: local Codex auth/cache area
- `.workspace/`: local run outputs and traces
- `projects/sample-service/`: generated project output

## Manual CLI Flow

If you want to run the pipeline without the dashboard:

```bash
python specyn.py validate --spec-dir specs/001-sample-service
python specyn.py compile-prompts --spec-dir specs/001-sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/001-sample-service --project-id sample-service --workspace .workspace/sample-service
```

Host-based helper modes:

```bash
python scripts/specyn_tasks.py dev
python scripts/specyn_tasks.py sample-dev
```

## Notes For First-Time Users

- Start Docker Desktop before `up -d` and `sample-up -d`
- Use `auth-status` and `doctor` before troubleshooting the UI
- The dashboard action button now lives in the Workspace page, not the Dashboard page
- Agent conversation shown in the Workspace UI is a filtered view of `agent_message` logs, not the full raw stream

## Documentation

- [Quickstart](docs/quickstart.md)
- [Operations](docs/operations.md)
- [CLI Run Reference](docs/cli-run-reference.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Local Development](guide/local-development.md)
