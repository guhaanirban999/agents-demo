"""Canned hotel inventory + system prompt for the dummy hotel agent."""

# A tiny, fixed catalog. Rates are per night in USD.
HOTELS = [
    {"name": "The Gotham Grand", "city": "New York", "area": "Midtown", "rate": 289, "stars": 4, "amenities": "wifi, gym, breakfast"},
    {"name": "Liberty Suites", "city": "New York", "area": "Downtown", "rate": 215, "stars": 3, "amenities": "wifi, kitchenette"},
    {"name": "Thames View Hotel", "city": "London", "area": "South Bank", "rate": 330, "stars": 4, "amenities": "wifi, gym, river view"},
    {"name": "Kensington Court", "city": "London", "area": "Kensington", "rate": 410, "stars": 5, "amenities": "wifi, spa, concierge"},
    {"name": "Sakura Inn", "city": "Tokyo", "area": "Shinjuku", "rate": 198, "stars": 3, "amenities": "wifi, onsen"},
    {"name": "Bay Bridge Hotel", "city": "San Francisco", "area": "Embarcadero", "rate": 275, "stars": 4, "amenities": "wifi, gym, bay view"},
]


def _format_inventory() -> str:
    lines = [
        f"- {h['name']} ({h['city']}, {h['area']}): {h['stars']}* ${h['rate']}/night "
        f"[{h['amenities']}]"
        for h in HOTELS
    ]
    return "\n".join(lines)


SYSTEM_PROMPT = f"""You are HotelBot, a hotel-booking assistant for a demo.
You can ONLY work with this fixed hotel inventory:

{_format_inventory()}

Behaviour:
- When asked to search, list the matching hotels from the inventory above.
- When asked to book, pick the best matching hotel and CONFIRM the reservation.
- Always invent an 8-character confirmation code (e.g. "Conf: HB-3K9P2A") for a booking.
- If nothing matches the requested city, say so and suggest the closest option.
- Be concise and friendly. This is a demo with fake data — never ask for payment
  details and never claim a real reservation was made.
"""
