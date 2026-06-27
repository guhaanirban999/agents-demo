"""Flight Booking A2A agent. Run: uvicorn agents.flight_booking.main:app"""

from agents.common import settings
from agents.common.agent_spec import build_card
from agents.common.a2a_app import build_app
from agents.common.claude_executor import ClaudeAgentExecutor
from agents.flight_booking.data import SYSTEM_PROMPT

BASE_URL = settings.public_url("http://localhost:8080")

card, legacy_card = build_card(
    name="Flight Booking Agent",
    description="Dummy A2A agent that searches and books flights over a fixed demo inventory.",
    version="1.0.0",
    organization="AgentFabric Demo",
    base_url=BASE_URL,
    documentation_url="https://github.com/your-org/agentfabric-demo",
    skills=[
        {
            "id": "search_flights",
            "name": "Search Flights",
            "description": "Find available flights between two airports.",
            "tags": ["travel", "flights", "search"],
            "examples": [
                "What flights are there from SFO to JFK?",
                "Find me a business class flight from JFK to London.",
            ],
        },
        {
            "id": "book_flight",
            "name": "Book Flight",
            "description": "Book a flight and return a confirmation PNR.",
            "tags": ["travel", "flights", "booking"],
            "examples": [
                "Book the morning flight from SFO to JFK.",
                "Book me on AF250 to London tonight.",
            ],
        },
    ],
)

executor = ClaudeAgentExecutor(system_prompt=SYSTEM_PROMPT)
app = build_app(card=card, legacy_card=legacy_card, executor=executor)
