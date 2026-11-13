#!/usr/bin/env bash
# Arranca la demo de KipuRest Live Vision en http://localhost:5000
set -euo pipefail
cd "$(dirname "$0")/../backend"
PORT="${KIPU_PORT:-5000}"

uv run python ../scripts/check_env.py || { echo "Corrige los problemas antes de la demo."; exit 1; }

uv run uvicorn app.main:app --host 127.0.0.1 --port "$PORT" --timeout-graceful-shutdown 2 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null; wait $SERVER 2>/dev/null' EXIT INT TERM

for _ in $(seq 1 60); do
  curl -fs "http://localhost:$PORT/api/health" >/dev/null 2>&1 && break
  sleep 1
done
URL="http://localhost:$PORT"
echo "Demo en $URL  (F = pantalla completa, C = calibrar, Ctrl+C = salir)"
[ -n "${KIPU_NO_BROWSER:-}" ] || xdg-open "$URL" >/dev/null 2>&1 || true
wait $SERVER
