# Quickstart

## 1. Install Prerequisites

Before the first run, install:

- Docker Desktop
- Python 3.11+ with `python` in PATH
- Node.js 20+ with npm

Check them:

```bash
python --version
node --version
npm --version
docker version
```

## 2. Run Initial Setup

From the repository root:

```bash
python specyn.py setup
python specyn.py auth-status
python specyn.py doctor
```

`setup` handles:

- `.env` creation/update
- auth mode selection
- ChatGPT login reuse or relogin
- OpenAI API key input for `openapi` mode
- model selection
- Docker agent validation when Docker Desktop is running

## 3. Start the Dashboard

```bash
python specyn.py up -d
```

Open:

- `http://localhost:4173`

Dashboard services:

- Frontend: `4173`
- Backend: `8180`
- AI Server: `8100`

## 4. Run Agents

Go to the `Workspace` page in the dashboard and run:

- `Run Agents And Generate sample-service`

The Workspace page now shows:

- filtered live `agent_message` text only
- expandable per-step details
- scrollable conversation area
- current progress and active agent

## 5. Start the Sample Runtime

```bash
python specyn.py sample-up -d
```

Open:

- `http://localhost:3000`
- `http://localhost:8080/api/v1/generated/sample-service/summary`
- `http://localhost:8000/generated/sample-service/context`

## 6. Stop Everything

```bash
python specyn.py down
python specyn.py sample-down
```

## 7. First-Time User Warnings

- Do not commit `.env`
- Do not commit `.specyn/codex`
- Do not expose `OPENAI_API_KEY`
- Do not upload raw logs without review
- If Docker Desktop is not started, `setup` may partially complete but stack startup will fail
