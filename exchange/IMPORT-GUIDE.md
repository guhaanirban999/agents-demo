# Importing the agents into Anypoint Exchange / Agent Fabric

Once both agents are deployed (see [`../deploy/DEPLOY.md`](../deploy/DEPLOY.md))
and their agent cards are reachable over HTTPS, register them in the Agent Fabric
**Agent Registry** so they appear in Exchange and the Agent Visualizer.

## What you're registering

Each agent serves its card at two paths:

| Path | Format | Use |
|---|---|---|
| `/.well-known/agent-card.json` | A2A **v1.0** (`supportedInterfaces`) | Default — try this first |
| `/.well-known/agent.json` | A2A **v0.3.0** (`url` / `preferredTransport`) | Fallback if your tenant expects the older shape |

Reference copies of both shapes are in this folder:
`agent-card-flight.v1.json`, `agent-card-flight.v0_3.json`, and the hotel
equivalents (their `url` is a placeholder — the live ones carry the real
deployed URL).

## Register by card URL (preferred)

1. Open **Anypoint Exchange** → **Agent Registry** (Agent Fabric).
2. Choose **Add / Register agent** → **By URL** (wording varies by release; it may
   sit under an Agent Scanner or a "Register external agent" action).
3. Paste the full card URL, e.g.
   `https://flight-booking-agent.onrender.com/.well-known/agent-card.json`
4. Agent Fabric fetches and validates the card, then catalogs the agent
   (name, description, skills, endpoint). Repeat for the hotel agent.
5. Confirm both agents show up in the **Agent Registry** and, if available in your
   tenant, in the **Agent Visualizer** topology.

> The endpoint must be **publicly reachable** at registration time — Agent Fabric
> pings the card URL to validate it. On Render's free tier, hit `/healthz` first to
> wake the service so validation doesn't time out on a cold start.

## Fallback: register as an agent asset (if URL import isn't offered)

Depending on your Agent Fabric release, "add external A2A agent by URL" may not be
exposed yet (some tenants only support MCP-server-by-URL). If so:

1. In Exchange, **Publish a new asset** of the closest available agent type
   (e.g. *A2A Agent* / *Agent*), or a generic asset if no agent type exists.
2. Set name/description to match the agent and attach the card JSON from this
   folder (use the `.v0_3.json` copy — the older shape is more widely accepted)
   as the asset's specification/metadata file.
3. Record the live endpoint URL in the asset's description so consumers can dial it.

## Demo narrative (optional)

- Show both agents live: run `test/smoke.sh <url>` to prove each books over A2A.
- Show them in the Agent Registry / Visualizer after import.
- Optional next step (configured in MuleSoft, not in this repo): add an **Agent
  Broker** that orchestrates both registered agents — "plan a trip" → calls the
  flight agent and the hotel agent — to demonstrate multi-agent orchestration.

## Troubleshooting

- **Validation fails / card not fetched:** the service is asleep or not public.
  Open the card URL in a browser; ensure it returns JSON. On Render, confirm the
  service is **Live** and `--allow-unauthenticated`-equivalent (Render web
  services are public by default).
- **Tenant rejects v1.0 card:** re-register using the `/.well-known/agent.json`
  (v0.3.0) URL.
- **Skills look wrong:** edit `skills=[...]` in the agent's `main.py`, redeploy,
  and re-register (or refresh the asset).
