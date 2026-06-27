#!/usr/bin/env bash
# Deploy both booking agents to Google Cloud Run from source.
#
# Prereqs (see deploy/DEPLOY.md):
#   - gcloud CLI installed + `gcloud auth login`
#   - a GCP project with billing, Cloud Run + Cloud Build APIs enabled
#   - ANTHROPIC_API_KEY exported (or in ../.env)
#
# Usage:
#   GCP_PROJECT=my-proj REGION=us-central1 deploy/deploy-cloudrun.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Pull ANTHROPIC_API_KEY from .env if not already in the environment.
if [[ -z "${ANTHROPIC_API_KEY:-}" && -f .env ]]; then
  set -a; source .env; set +a
fi

: "${GCP_PROJECT:?set GCP_PROJECT to your Google Cloud project id}"
: "${ANTHROPIC_API_KEY:?set ANTHROPIC_API_KEY (or put it in .env)}"
REGION="${REGION:-us-central1}"
MODEL="${MODEL:-claude-haiku-4-5}"

deploy_one() {
  local service="$1" agent_module="$2"
  echo ">>> Deploying $service ($agent_module) ..."

  # First deploy (creates the service + URL). PUBLIC_URL is unknown yet.
  # --source . builds the root Dockerfile; AGENT_MODULE selects which agent.
  gcloud run deploy "$service" \
    --project "$GCP_PROJECT" --region "$REGION" \
    --source . \
    --allow-unauthenticated \
    --set-env-vars "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY},MODEL=${MODEL},AGENT_MODULE=${agent_module}"

  # Learn the assigned URL, then redeploy so the agent card advertises it.
  local url
  url="$(gcloud run services describe "$service" \
        --project "$GCP_PROJECT" --region "$REGION" --format='value(status.url)')"
  echo ">>> $service URL: $url  (setting PUBLIC_URL and redeploying)"

  gcloud run services update "$service" \
    --project "$GCP_PROJECT" --region "$REGION" \
    --update-env-vars "PUBLIC_URL=${url}"

  echo ">>> $service agent card: ${url}/.well-known/agent-card.json"
}

deploy_one flight-booking-agent agents.flight_booking.main
deploy_one hotel-booking-agent  agents.hotel_booking.main

echo
echo "Done. Import these card URLs into Anypoint Exchange (see exchange/IMPORT-GUIDE.md):"
echo "  flight: https://flight-booking-agent-<hash>-<region>.run.app/.well-known/agent-card.json"
echo "  hotel:  https://hotel-booking-agent-<hash>-<region>.run.app/.well-known/agent-card.json"
