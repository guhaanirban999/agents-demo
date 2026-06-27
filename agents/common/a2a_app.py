"""Assemble a FastAPI app that speaks A2A for a given card + executor.

Exposes:
  GET  /.well-known/agent-card.json   A2A v1.0 card (served by the SDK)
  GET  /.well-known/agent.json        v0.3.0-style card (compat alias)
  POST /                              A2A JSON-RPC endpoint (message/send, etc.)
  /v1/*                               A2A REST endpoints
  GET  /healthz                       liveness probe
"""

from typing import Any

from fastapi import FastAPI
from starlette.responses import JSONResponse

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
    create_rest_routes,
)
import a2a.types as t

from agents.common.claude_executor import ClaudeAgentExecutor


def build_app(
    *,
    card: t.AgentCard,
    legacy_card: dict[str, Any],
    executor: ClaudeAgentExecutor,
) -> FastAPI:
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        agent_card=card,
    )

    app = FastAPI(title=card.name, version=card.version)

    # enable_v0_3_compat=True lets the same endpoints serve both A2A v1.0 and
    # v0.3.0 clients, which maximizes interoperability with whatever the
    # registering platform speaks.
    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=create_agent_card_routes(card),
        jsonrpc_routes=create_jsonrpc_routes(handler, rpc_url="/", enable_v0_3_compat=True),
        rest_routes=create_rest_routes(handler, enable_v0_3_compat=True),
    )

    @app.get("/.well-known/agent.json", tags=["A2A: Agent Card"])
    async def legacy_agent_card() -> JSONResponse:
        """v0.3.0-style card for consumers that expect the older format/path."""
        return JSONResponse(legacy_card)

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    # The SDK mounts a catch-all `/{tenant}` route that otherwise swallows any
    # multi-segment path registered after it (e.g. /.well-known/agent.json).
    # Move our custom routes ahead of that mount so they match first.
    our_paths = {"/.well-known/agent.json", "/healthz"}
    ours = [r for r in app.router.routes if getattr(r, "path", None) in our_paths]
    for r in ours:
        app.router.routes.remove(r)
    app.router.routes[:0] = ours

    return app
