"""Canned flight inventory + system prompt for the dummy flight agent."""

# A tiny, fixed catalog. Prices in USD. Times are local.
FLIGHTS = [
    {"flight": "AF101", "from": "SFO", "to": "JFK", "depart": "08:00", "arrive": "16:25", "price": 312, "class": "Economy"},
    {"flight": "AF102", "from": "SFO", "to": "JFK", "depart": "13:30", "arrive": "21:55", "price": 358, "class": "Economy"},
    {"flight": "AF250", "from": "JFK", "to": "LHR", "depart": "21:10", "arrive": "09:05", "price": 540, "class": "Economy"},
    {"flight": "AF255", "from": "JFK", "to": "LHR", "depart": "18:40", "arrive": "06:35", "price": 880, "class": "Business"},
    {"flight": "AF300", "from": "SFO", "to": "NRT", "depart": "11:20", "arrive": "15:40", "price": 720, "class": "Economy"},
    {"flight": "AF410", "from": "LHR", "to": "CDG", "depart": "07:15", "arrive": "09:35", "price": 145, "class": "Economy"},
]


def _format_inventory() -> str:
    lines = [
        f"- {f['flight']}: {f['from']}->{f['to']} dep {f['depart']} arr {f['arrive']} "
        f"{f['class']} ${f['price']}"
        for f in FLIGHTS
    ]
    return "\n".join(lines)


SYSTEM_PROMPT = f"""You are FlightBot, a flight-booking assistant for a demo.
You can ONLY work with this fixed flight inventory:

{_format_inventory()}

Behaviour:
- When asked to search, list the matching flights from the inventory above.
- When asked to book, pick the best matching flight and CONFIRM the booking.
- Always invent a 6-character alphanumeric PNR (e.g. "PNR: 7QX4K2") for a booking.
- If nothing matches, say so and suggest the closest available option.
- Be concise and friendly. This is a demo with fake data — never ask for payment
  details and never claim a real reservation was made.
"""
