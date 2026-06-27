"""Build A2A agent cards from a simple skill description.

`a2a-sdk` 1.x implements A2A protocol v1.0, whose card uses `supportedInterfaces`
(served at /.well-known/agent-card.json). Some consumers — possibly including a
given Anypoint Agent Fabric tenant — still expect the older v0.3.0 card shape with
a top-level `url`/`preferredTransport`. To hedge that uncertainty we generate BOTH
from the same inputs: the SDK proto card (canonical) and a v0.3.0-style dict that
the app also serves at the legacy /.well-known/agent.json path.
"""

from typing import Any

import a2a.types as t


def build_card(
    *,
    name: str,
    description: str,
    version: str,
    organization: str,
    base_url: str,
    skills: list[dict[str, Any]],
    documentation_url: str | None = None,
) -> tuple[t.AgentCard, dict[str, Any]]:
    """Return (proto AgentCard for v1.0, dict for v0.3.0) built from `skills`.

    Each skill dict: {id, name, description, tags?, examples?}.
    """
    proto_skills = [
        t.AgentSkill(
            id=s["id"],
            name=s["name"],
            description=s["description"],
            tags=s.get("tags", []),
            examples=s.get("examples", []),
        )
        for s in skills
    ]

    card = t.AgentCard(
        name=name,
        description=description,
        version=version,
        documentation_url=documentation_url or "",
        provider=t.AgentProvider(organization=organization, url=base_url),
        supported_interfaces=[
            t.AgentInterface(
                url=base_url,
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            )
        ],
        capabilities=t.AgentCapabilities(streaming=False, push_notifications=False),
        default_input_modes=["text/plain", "application/json"],
        default_output_modes=["text/plain", "application/json"],
        skills=proto_skills,
    )

    legacy: dict[str, Any] = {
        "protocolVersion": "0.3.0",
        "name": name,
        "description": description,
        "url": base_url,
        "preferredTransport": "JSONRPC",
        "version": version,
        "provider": {"organization": organization, "url": base_url},
        "capabilities": {"streaming": False, "pushNotifications": False},
        "defaultInputModes": ["text/plain", "application/json"],
        "defaultOutputModes": ["text/plain", "application/json"],
        "skills": [
            {
                "id": s["id"],
                "name": s["name"],
                "description": s["description"],
                "tags": s.get("tags", []),
                "examples": s.get("examples", []),
            }
            for s in skills
        ],
    }
    if documentation_url:
        legacy["documentationUrl"] = documentation_url

    return card, legacy
