#!/usr/bin/env bash
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0
#
# Runs every demo in presentation order, unattended, against a running EPR.
# Use it to rehearse before a talk. It stops at the first failure.
#
# Usage:
#   demos/scripts/run_all.sh                 # EPR at http://localhost:8042
#   EPR_URL=http://epr:8042 demos/scripts/run_all.sh
#   demos/scripts/run_all.sh --skip-generate # leave EPR's data alone (skips the 55 posts)
#
# Needs: uv, curl, and EPR running (see docs/tutorials/code/docker-compose.yaml).
# Creates data in EPR: 11 receivers and 44 events (unless skipped) plus 1 receiver
# and 1 event from the client demo. Reset with `docker compose down -v`.

set -euo pipefail

cd "$(dirname "$0")/../.."

EPR_URL="${EPR_URL:-http://localhost:8042}"
SKIP_GENERATE=0
for arg in "$@"; do
  case "$arg" in
    --skip-generate) SKIP_GENERATE=1 ;;
    -h | --help)
      sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 2
      ;;
  esac
done

section() {
  printf '\n==== %s ====\n' "$1"
}

fail() {
  printf '\nFAILED: %s\n' "$1" >&2
  exit 1
}

section "Prerequisites"
command -v uv > /dev/null || fail "uv is not installed (https://docs.astral.sh/uv/)"
command -v curl > /dev/null || fail "curl is not installed"
if ! curl -fsS --max-time 5 "${EPR_URL}/healthz/readiness" > /dev/null; then
  fail "EPR is not ready at ${EPR_URL}. Start it with: (cd docs/tutorials/code && docker compose up -d --build)"
fi
echo "uv: $(uv --version)"
echo "EPR is ready at ${EPR_URL}"

section "Demo 1: generate_epr_events.py --dry-run (prints curl commands, changes nothing)"
dry_run_output="$(uv run python demos/generate_epr_events.py --dry-run --url "${EPR_URL}")"
curl_count="$(printf '%s\n' "${dry_run_output}" | grep -c '^curl ')"
printf '%s\n' "${dry_run_output}" | grep '^curl ' | head -n 2 | cut -c 1-160
echo "..."
[ "${curl_count}" -eq 55 ] || fail "expected 55 curl commands (11 receivers + 44 events), found ${curl_count}"
echo "OK: ${curl_count} curl commands"

if [ "${SKIP_GENERATE}" -eq 1 ]; then
  section "Demo 1b: posting events (skipped)"
else
  section "Demo 1b: generate_epr_events.py (posts 11 receivers and 44 events)"
  uv run python demos/generate_epr_events.py --url "${EPR_URL}" 2>&1 | tail -n 3
fi

section "Demo 2: openapi_demo.py (HTTP endpoints, OpenAPI documents, tool list)"
uv run python demos/openapi_demo.py --epr-url "${EPR_URL}"

section "Demo 3: mcp_client_demo.py (create, fetch, and search through MCP tools)"
uv run python demos/mcp_client_demo.py --epr-url "${EPR_URL}"

section "All demos passed"
