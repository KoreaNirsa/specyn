# Troubleshooting

## `setup` works but `up -d` fails

This usually means Docker Desktop is installed but not running, or the Docker engine is not ready yet.

Typical Windows error:

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
```

Recommended order:

```bash
python specyn.py setup
python specyn.py auth-status
python specyn.py doctor

# start Docker Desktop

python specyn.py up -d
```

## Dashboard frontend exits immediately

Check:

```bash
docker compose -f docker-compose.local.yml ps
docker compose -f docker-compose.local.yml logs --tail 200 dashboard-frontend
```

Expected dashboard URL:

- `http://localhost:4173`

## Auth was configured but requests are not working

Check:

```bash
python specyn.py auth-status
```

Review:

- selected auth mode
- whether `OPENAI_API_KEY` is set for `openapi`
- whether Docker Desktop is running for Docker-based auth reuse

## Sensitive files were exposed by mistake

If `.env` or auth cache was exposed:

1. Remove it from any commit or upload immediately
2. Rotate `OPENAI_API_KEY` if applicable
3. Re-run `python specyn.py setup` if you need to restore local auth state

## Sample runtime is not reachable

Check:

```bash
python specyn.py sample-up -d
docker compose -f docker-compose.local.yml ps
```

Expected sample URLs:

- `http://localhost:3000`
- `http://localhost:8080/api/v1/generated/sample-service/summary`
- `http://localhost:8000/generated/sample-service/context`
