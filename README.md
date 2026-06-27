# agents-demo — Flight & Hotel Booking A2A Agents

Two **dummy A2A agents** — a **Flight Booking Agent** and a **Hotel Booking
Agent** — built with the **Anthropic SDK** (Claude) and the **`a2a-sdk`**. Each
serves an **A2A agent card** at a public URL so it can be registered in **MuleSoft
Anypoint Exchange / Agent Fabric** for an Agent Fabric demo use case.

Each agent answers A2A messages by calling Claude over a small, hardcoded travel
inventory — it "searches" and "books" with fake confirmation codes. No real
travel APIs, payments, or persistence.

## Architecture

```
                 A2A message/send (JSON-RPC or REST)
   client ───────────────────────────────────────────►  ┌─────────────────────┐
                                                         │ Flight Booking Agent │  FastAPI + a2a-sdk
   /.well-known/agent-card.json (A2A v1.0)  ◄────────────│  ClaudeAgentExecutor │──► Claude (Anthropic SDK)
   /.well-known/agent.json      (v0.3.0 compat)          └─────────────────────┘
                                                         ┌─────────────────────┐
   (same shape)                                          │ Hotel Booking Agent  │
                                                         └─────────────────────┘
        │ deploy (Render / Cloud Run)        │ register card URL
        ▼                                    ▼
   public HTTPS URLs  ───────────────────►  Anypoint Exchange / Agent Fabric Registry
```

Two independent services (two hostnames) because the A2A well-known card path is
per-host.

## Layout

```
agents/
  common/        a2a_app.py (FastAPI wiring) · claude_executor.py · agent_spec.py · settings.py
  flight_booking/ main.py · data.py (inventory + system prompt)
  hotel_booking/  main.py · data.py
render.yaml      Render Blueprint — deploys BOTH agents
Dockerfile       one image, AGENT_MODULE picks the agent (Cloud Run / docker)
deploy/          DEPLOY.md (Render-first) · deploy-cloudrun.sh
exchange/        IMPORT-GUIDE.md · sample agent cards (v1.0 + v0.3.0)
test/            smoke.sh — fetch cards + live message/send
```

## Endpoints (per agent)

| Method | Path | Purpose |
|---|---|---|
| GET | `/.well-known/agent-card.json` | A2A v1.0 agent card |
| GET | `/.well-known/agent.json` | v0.3.0-style card (compat) |
| POST | `/` | A2A JSON-RPC (`message/send`, `tasks/get`, …) |
| * | `/v1/*` | A2A REST endpoints |
| GET | `/healthz` | liveness / pre-warm |

The card is served in **A2A v1.0** form (the `a2a-sdk` 1.x default); the v0.3.0
alias hedges against a tenant that expects the older shape. The RPC/REST routes
run with `enable_v0_3_compat=True` so both protocol versions work.

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then put your ANTHROPIC_API_KEY in .env
set -a; source .env; set +a

# flight on 8080, hotel on 8081
uvicorn agents.flight_booking.main:app --port 8080 &
uvicorn agents.hotel_booking.main:app  --port 8081 &

test/smoke.sh http://localhost:8080
PROMPT="Book a 5 star hotel in London" test/smoke.sh http://localhost:8081
```

Example live response (Claude-backed):
> *"Perfect! I've booked you on the morning flight from SFO to JFK. Flight: AF101 …
> PNR: 3M7X9K"*

## Deploy + register

1. **Deploy** both agents → [`deploy/DEPLOY.md`](deploy/DEPLOY.md) (Render
   recommended; Cloud Run alternative included).
2. **Register** each card URL in Agent Fabric → [`exchange/IMPORT-GUIDE.md`](exchange/IMPORT-GUIDE.md).

## Configuration

| Env var | Default | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | required |
| `MODEL` | `claude-haiku-4-5` | use `claude-sonnet-4-6` for higher quality |
| `PUBLIC_URL` | auto | the card's `url`; auto-set from `RENDER_EXTERNAL_URL` on Render |
| `PORT` | `8080` | set by the platform |

## Notes & caveats

- **A2A protocol version:** `a2a-sdk` 1.1.0 implements A2A **v1.0** (card uses
  `supportedInterfaces`). The v0.3.0 alias is provided for compatibility.
- **Exchange import step varies by tenant.** Some Agent Fabric releases expose
  "register external A2A agent by URL"; others currently only do MCP-server-by-URL.
  The import guide covers the URL path and an asset-upload fallback. What this repo
  guarantees is the prerequisite either way: a live, valid agent card at a stable
  public URL.
- **Dummy by design:** inventories live in `agents/*/data.py`; edit them (or the
  system prompts) and redeploy to change agent behaviour.
