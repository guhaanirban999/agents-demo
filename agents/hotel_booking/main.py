"""Hotel Booking A2A agent. Run: uvicorn agents.hotel_booking.main:app"""

from agents.common import settings
from agents.common.agent_spec import build_card
from agents.common.a2a_app import build_app
from agents.common.claude_executor import ClaudeAgentExecutor
from agents.hotel_booking.data import SYSTEM_PROMPT

BASE_URL = settings.public_url("http://localhost:8080")

card, legacy_card = build_card(
    name="Hotel Booking Agent",
    description="Dummy A2A agent that searches and books hotels over a fixed demo inventory.",
    version="1.0.0",
    organization="AgentFabric Demo",
    base_url=BASE_URL,
    documentation_url="https://github.com/your-org/agentfabric-demo",
    skills=[
        {
            "id": "search_hotels",
            "name": "Search Hotels",
            "description": "Find available hotels in a city.",
            "tags": ["travel", "hotels", "search"],
            "examples": [
                "What hotels do you have in London?",
                "Find a 5 star hotel in Kensington.",
            ],
        },
        {
            "id": "book_hotel",
            "name": "Book Hotel",
            "description": "Book a hotel and return a confirmation code.",
            "tags": ["travel", "hotels", "booking"],
            "examples": [
                "Book the Gotham Grand in New York.",
                "Reserve a room near the South Bank in London.",
            ],
        },
    ],
)

executor = ClaudeAgentExecutor(system_prompt=SYSTEM_PROMPT)
app = build_app(card=card, legacy_card=legacy_card, executor=executor)
