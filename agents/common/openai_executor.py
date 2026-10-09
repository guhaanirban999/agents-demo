"""An A2A AgentExecutor backed by OpenAI (drop-in replacement for ClaudeAgentExecutor)."""

import os
from openai import AsyncOpenAI

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.helpers import new_text_message


class OpenAIAgentExecutor(AgentExecutor):
    """Immediate-response executor: read user text -> ask OpenAI -> enqueue reply."""

    def __init__(self, system_prompt: str, model: str | None = None) -> None:
        self._system = system_prompt
        self._model = model or os.environ.get("MODEL", "gpt-4o-mini")
        # AsyncOpenAI reads OPENAI_API_KEY from the environment.
        self._client = AsyncOpenAI()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = (context.get_user_input() or "").strip() or "Hello"
        reply = await self._ask_openai(user_text)
        await event_queue.enqueue_event(
            new_text_message(
                reply,
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        return

    async def _ask_openai(self, user_text: str) -> str:
        resp = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": self._system},
                {"role": "user", "content": user_text},
            ],
        )
        return resp.choices[0].message.content or "(the agent produced no text response)"
