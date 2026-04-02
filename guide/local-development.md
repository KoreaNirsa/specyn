# Local Development

## Prerequisites

Install before local development:

- Docker Desktop
- Python 3.11+
- Node.js 20+ and npm

Useful checks:

```bash
python --version
node --version
npm --version
docker version
```

## Standard Local Flow

```bash
python specyn.py setup
python specyn.py auth-status
python specyn.py doctor
python specyn.py up -d
python specyn.py sample-up -d
```

If Docker Desktop is not running, `setup` may still update `.env`, but Docker-backed validation and service startup will not complete.

## Dashboard Stack

- Frontend: `http://localhost:4173`
- Backend: `http://localhost:8180`
- AI Server: `http://localhost:8100`

## Sample Stack

- Frontend: `http://localhost:3000`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- AI context: `http://localhost:8000/generated/sample-service/context`

## Manual Spec Flow

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
```

## Security and Hygiene

- Never commit `.env`
- Never commit `.specyn/codex`
- Treat `.workspace/` as local output
- Review generated code before promoting it into a shared branch
- Review logs before copying them into tickets or chats

## Local Dev Alternatives

These are host-based helper modes and are secondary to Docker Compose:

```bash
python scripts/specyn_tasks.py dev
python scripts/specyn_tasks.py sample-dev
```
