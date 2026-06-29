# Deploying the booking agents

You need two public HTTPS URLs (one per agent) so their agent cards can be
registered in Anypoint Exchange / Agent Fabric.

- **Primary: Render** (below) — no CLI to install, real free tier, deploys
  straight from a Git repo, and injects the public URL for you.
- **Alternative: Google Cloud Run** — see the bottom of this file.

---

## Render (recommended)

Render gives each service a stable `https://<service>.onrender.com` URL and sets
`RENDER_EXTERNAL_URL`, which the agent card reads automatically — so there's no
post-deploy URL editing.

### 1. Put this project in a Git repo

Render deploys from GitHub/GitLab/Bitbucket. Push this folder to a repo:

```bash
cd /Users/anirbanguha/ClaudeWS/agents-demo
git init && git add . && git commit -m "Flight & hotel A2A agents for Agent Fabric demo"
# create a repo on GitHub, then:
git remote add origin https://github.com/<you>/agentfabric-demo.git
git push -u origin main
```

`.env` is git-ignored, so your key is not pushed.

### 2. Deploy both agents via the Blueprint

1. In the Render dashboard: **New +** → **Blueprint**.
2. Connect the repo. Render detects [`render.yaml`](../render.yaml) and shows two
   services: `flight-booking-agent` and `hotel-booking-agent`.
3. When prompted, paste your **`ANTHROPIC_API_KEY`** (applies to both services;
   it's marked `sync:false` so it's never stored in the repo).
4. **Apply** — Render builds and deploys both.

Resulting card URLs:
- `https://flight-booking-agent.onrender.com/.well-known/agent-card.json`
- `https://hotel-booking-agent.onrender.com/.well-known/agent-card.json`

(Exact subdomains may get a suffix if the names are taken — copy them from the
Render dashboard.)

### 3. Verify

```bash
test/smoke.sh https://flight-booking-agent.onrender.com
PROMPT="Find hotels in London" test/smoke.sh https://hotel-booking-agent.onrender.com
```

### Render notes
- **Free tier sleeps** after ~15 min idle; the next request (including the card
  fetch) wakes it with a ~30–50s cold start. Fine for a demo. Upgrade to a paid
  instance ($7/mo) for always-on.
- **Before a live demo:** run `deploy/warmup.sh` (~2 min ahead). It wakes both
  dynos (polls `/healthz` through the cold start) and does a real `message/send`
  to warm the Claude path, then prints `🎉 Both agents warm`. Pass custom URLs as
  args if your `*.onrender.com` hostnames differ. To keep them warm for the whole
  demo window instead, run `deploy/keepalive.sh`.
- **Secret:** `ANTHROPIC_API_KEY` is the only secret. Set/rotate it under each
  service's **Environment** tab.
- **No Docker needed** — the Blueprint uses Render's native Python runtime. (A
  root `Dockerfile` is included if you prefer `runtime: docker`.)

---

## Alternative: Google Cloud Run

`gcloud` is **not** installed on this machine. If you'd rather use Cloud Run:

```bash
brew install --cask google-cloud-sdk
gcloud auth login && gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

export GCP_PROJECT=YOUR_PROJECT_ID
deploy/deploy-cloudrun.sh
```

`deploy/deploy-cloudrun.sh` builds the root `Dockerfile` (one image, `AGENT_MODULE`
selects the agent), deploys both services, and sets `PUBLIC_URL` to each assigned
`*.run.app` URL. See the script for Secret Manager and cost notes.
