# One image runs either agent. Pick which via the AGENT_MODULE env var:
#   agents.flight_booking.main  (default)  |  agents.hotel_booking.main
#
# Local:
#   docker build -t booking-agent .
#   docker run -p 8080:8080 -e ANTHROPIC_API_KEY=sk-... \
#     -e AGENT_MODULE=agents.hotel_booking.main booking-agent
#
# Cloud Run uses this Dockerfile automatically via `gcloud run deploy --source .`.
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/ ./agents/

ENV PORT=8080
ENV AGENT_MODULE=agents.flight_booking.main
EXPOSE 8080

CMD ["sh", "-c", "uvicorn ${AGENT_MODULE}:app --host 0.0.0.0 --port ${PORT}"]
