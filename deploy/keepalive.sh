#!/usr/bin/env bash
# Keep the free-tier Render agents awake during a demo by pinging /healthz.
#
# Render free instances sleep after ~15 min idle (then cold-start ~30-50s).
# Pinging every 10 min keeps them warm.
#
# NOTE: Render free tier is ~750 instance-hours/month TOTAL. Two services kept
# awake 24/7 (~1440 hrs) exceeds that. Run this during your demo window and stop
# it (Ctrl-C) when done — don't leave it running permanently on the free plan.
#
# Usage:
#   deploy/keepalive.sh                 # ping default agents every 600s
#   INTERVAL=300 deploy/keepalive.sh    # every 5 min
#   deploy/keepalive.sh URL1 URL2 ...   # custom base URLs
set -euo pipefail

INTERVAL="${INTERVAL:-600}"

if [[ $# -gt 0 ]]; then
  URLS=("$@")
else
  URLS=(
    "https://flight-booking-agent-bq9s.onrender.com"
    "https://hotel-booking-agent-cr9b.onrender.com"
  )
fi

echo "keepalive: pinging ${#URLS[@]} agents every ${INTERVAL}s (Ctrl-C to stop)"
while true; do
  ts="$(date '+%Y-%m-%d %H:%M:%S')"
  for u in "${URLS[@]}"; do
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 60 "$u/healthz" || echo 000)"
    echo "[$ts] $u/healthz -> $code"
  done
  sleep "$INTERVAL"
done
