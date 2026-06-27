#!/usr/bin/env bash
# Smoke-test an A2A booking agent: fetch both agent cards and run a live
# message/send (which calls Claude). Works against a local or deployed URL.
#
# Usage:
#   test/smoke.sh                         # defaults to http://localhost:8080
#   test/smoke.sh https://my-agent.run.app
#   PROMPT="Find hotels in London" test/smoke.sh https://hotel-...run.app
set -euo pipefail

BASE="${1:-http://localhost:8080}"
PROMPT="${PROMPT:-Book me the morning flight from SFO to JFK}"

echo "== GET $BASE/healthz =="
curl -sf "$BASE/healthz" && echo

echo "== GET $BASE/.well-known/agent-card.json (A2A v1.0) =="
curl -sf "$BASE/.well-known/agent-card.json" | head -c 400; echo "..."

echo "== GET $BASE/.well-known/agent.json (v0.3.0 compat) =="
curl -sf "$BASE/.well-known/agent.json" | head -c 200; echo "..."

echo "== POST $BASE/ (A2A JSON-RPC message/send) =="
curl -sf -X POST "$BASE/" \
  -H 'Content-Type: application/json' \
  -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"message/send\",\"params\":{\"message\":{\"role\":\"user\",\"kind\":\"message\",\"messageId\":\"smoke-1\",\"parts\":[{\"kind\":\"text\",\"text\":\"${PROMPT}\"}]}}}"
echo
echo "== OK =="
