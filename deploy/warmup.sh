#!/usr/bin/env bash
# Pre-demo warm-up for the free-tier Render agents.
#
# Render free instances sleep after ~15 min idle, then cold-start ~30-50s. Run
# this ~2 min before a demo so the FIRST /travel of the demo is fast. For each
# agent it: (1) wakes the dyno by polling /healthz until 200, then (2) sends a
# real A2A message/send so the Anthropic (Claude Haiku) path is warm too. Both
# agents are warmed in parallel, so total time ~= one cold start (~60-90s).
#
# The message/send calls Claude (Haiku) — fractions of a cent per run. /healthz
# alone is free; see keepalive.sh if you only want to keep dynos awake.
#
# Usage:
#   deploy/warmup.sh                          # warm the default agents
#   deploy/warmup.sh <flightUrl> <hotelUrl>   # custom base URLs (no trailing /)
#   BUDGET=200 deploy/warmup.sh               # allow up to 200s per dyno to wake
#
# Exit code is non-zero if either agent is not READY, so you know before going live.
set -uo pipefail

FLIGHT="${1:-https://flight-booking-agent-bq9s.onrender.com}"
HOTEL="${2:-https://hotel-booking-agent-cr9b.onrender.com}"
BUDGET="${BUDGET:-150}"   # max seconds to wait for a dyno to wake

# warm <base-url> <prompt> <label>
warm() {
  local url="$1" prompt="$2" label="$3" t0 woke r1 body
  t0=$SECONDS

  # Phase 1 — wake the dyno (absorbs the 30-50s Render cold start).
  until [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 60 "$url/healthz" || echo 000)" = "200" ]; do
    if [ $((SECONDS - t0)) -ge "$BUDGET" ]; then
      echo "❌ $label NOT READY — no /healthz 200 within ${BUDGET}s ($url)"
      return 1
    fi
    sleep 5
  done
  woke=$((SECONDS - t0))

  # Phase 2 — warm the Claude path with a real message/send (payload from smoke.sh).
  r1=$SECONDS
  body="$(curl -s --max-time 90 -X POST "$url/" \
    -H 'Content-Type: application/json' \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"message/send\",\"params\":{\"message\":{\"role\":\"user\",\"kind\":\"message\",\"messageId\":\"warmup-1\",\"parts\":[{\"kind\":\"text\",\"text\":\"${prompt}\"}]}}}")"
  if echo "$body" | grep -q '"result"'; then
    echo "✅ $label READY (woke ${woke}s, round-trip $((SECONDS - r1))s)"
    return 0
  fi
  echo "❌ $label woke but message/send failed: $(echo "$body" | head -c 200)"
  return 1
}

echo "Warming agents in parallel (wake budget ${BUDGET}s each)…"
warm "$FLIGHT" "Book me the morning flight from SFO to JFK" "flight-agent" & pf=$!
warm "$HOTEL"  "Find hotels in London"                       "hotel-agent"  & ph=$!
wait "$pf"; rf=$?
wait "$ph"; rh=$?

if [ "$rf" -eq 0 ] && [ "$rh" -eq 0 ]; then
  echo "🎉 Both agents warm — ready for demo."
  exit 0
fi
echo "⚠️  One or more agents not ready — re-run, raise BUDGET, or check the Render dashboard."
exit 1
