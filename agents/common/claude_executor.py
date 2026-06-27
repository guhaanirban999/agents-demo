"""An A2A AgentExecutor whose logic is a single Claude call.

The agents are intentionally "dummy": each one answers an incoming A2A message by
asking Claude to play a travel-booking assistant over a small, hardcoded inventory
that is baked into the system prompt. No real reservations, payments, or external
APIs are involved.
"""

from anthropic import AsyncAnthropic

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.helpers import new_text_message

from agents.common import settings


class ClaudeAgentExecutor(AgentExecutor):
    """Immediate-response executor: read user text -> ask Claude -> enqueue reply."""

    def __init__(self, system_prompt: str, model: str | None = None) -> None:
        self._system = system_prompt
        self._model = model or settings.MODEL
        # AsyncAnthropic reads ANTHROPIC_API_KEY from the environment.
        self._client = AsyncAnthropic()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = (context.get_user_input() or "").strip() or "Hello"
        reply = await self._ask_claude(user_text)
        await event_queue.enqueue_event(
            new_text_message(
                reply,
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # Replies are produced in a single call, so there is nothing long-running
        # to cancel. Returning is sufficient for this demo.
        return

    async def _ask_claude(self, user_text: str) -> str:
        resp = await self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=self._system,
            messages=[{"role": "user", "content": user_text}],
        )
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", None) == "text"
        )
        return text or "(the agent produced no text response)"
