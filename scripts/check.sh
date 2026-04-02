#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if command -v python3 >/dev/null 2>&1; then
  exec python3 scripts/specyn_tasks.py ci-local
elif command -v python >/dev/null 2>&1; then
  exec python scripts/specyn_tasks.py ci-local
elif command -v py >/dev/null 2>&1; then
  exec py -3 scripts/specyn_tasks.py ci-local
else
  echo "[specyn] Python 3.12+를 찾을 수 없습니다."
  exit 1
fi
