"""Runtime configuration, read from environment variables.

The only required secret is ANTHROPIC_API_KEY. Everything else has a sensible
default so the agents run locally with zero configuration.
"""

import os


# Claude model used by every agent. Haiku is cheap + fast, which is plenty for a
# dummy demo. Bump to "claude-sonnet-4-6" for higher-quality replies.
MODEL = os.environ.get("MODEL", "claude-haiku-4-5")

# Cloud Run injects PORT; default 8080 matches the container contract.
PORT = int(os.environ.get("PORT", "8080"))


def public_url(default: str) -> str:
    """The externally reachable base URL of this agent.

    This value is written into the agent card (the `url` clients dial and the
    address MuleSoft stores at registration). Resolution order:
      1. PUBLIC_URL            — explicit override (any platform)
      2. RENDER_EXTERNAL_URL   — injected automatically by Render
      3. `default`             — e.g. http://localhost:8080 for local runs
    """
    url = (
        os.environ.get("PUBLIC_URL")
        or os.environ.get("RENDER_EXTERNAL_URL")
        or default
    )
    return url.rstrip("/")
