from __future__ import annotations

import logging

import instructor
from openai import AsyncOpenAI

from mycoportal_agent.planning.models import PlannerOutput, ToolPlan
from mycoportal_agent.planning.registry import registry

logger = logging.getLogger(__name__)


class MycoPortalPlanner:
    """LLM-driven planner for MycoPortal v1 read-only scope."""

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = instructor.from_openai(openai_client)
        self._system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        return f"""
You are a biodiversity research planner for the MycoPortal (Symbiota) API.

Your job:
1. Understand what the user is asking
2. Select the right tool(s) to answer the query
3. Explain your reasoning clearly

## AVAILABLE TOOLS

{registry.get_all_for_planner()}

## RULES

**Intent selection:**
- Choose exactly one primary intent
- Use "unknown" only when the query is genuinely ambiguous
- Use "out_of_scope" for write operations or non-MycoPortal requests

**Tool selection:**
- Plan only tools needed to answer the user
- Tag as must_call if required
- Tag as optional only when it enriches the response

**Clarification:**
- Ask clarification only when required identifiers or search terms are missing
- Keep clarification question specific and short

**Read-only scope:**
- This agent is read-only
- Any create/update/delete request is out_of_scope

**Reasoning:**
- Provide at least one sentence explaining tool choice
"""


    async def plan(self, query: str) -> PlannerOutput:
        logger.warning("[MYCO-PLANNER] Planning query: %s", query)

        result = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": query},
            ],
            response_model=PlannerOutput,
            max_retries=2,
        )

        logger.warning("[MYCO-PLANNER] Intent: %s", result.intent)
        logger.warning(
            "[MYCO-PLANNER] Tools: %s",
            [(t.tool_name, t.priority) for t in result.tools_planned],
        )
        logger.warning("[MYCO-PLANNER] Reasoning: %s", result.reasoning)
        if result.clarification_needed:
            logger.warning(
                "[MYCO-PLANNER] Clarification needed: %s",
                result.clarification_question,
            )

        return result
