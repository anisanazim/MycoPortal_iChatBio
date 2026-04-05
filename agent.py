from ichatbio.agent import IChatBioAgent
from ichatbio.agent_response import ResponseContext
from ichatbio.types import AgentCard, AgentEntrypoint
import logging
from typing import Optional
from openai import AsyncOpenAI
from typing_extensions import override
from common.config import get_config_value
from pydantic import BaseModel, Field
from planning.planner import MycoPortalPlanner
from extraction.extractor import MycoPortalExtractor
from resolution.resolver import MycoPortalResolver
from routing.router import MycoPortalRouter
from execution.executor import MycoPortalExecutor
from client.api import MycoPortalAPI

logger = logging.getLogger(__name__)


class MycoPortalParams(BaseModel):
    """Parameters for MycoPortal agent queries."""
    query: str = Field(
        ...,
        description="Natural language query about fungal biodiversity (occurrences, species, distributions, etc.)"
    )
    context: Optional[str] = Field(
        None,
        description="Additional context or specific requirements"
    )


class MycoPortalAgent(IChatBioAgent):
    """MycoPortal fungal biodiversity agent with LLM-driven planning and extraction."""

    def __init__(self):
        """Initialize agent with five-stage pipeline (deferred OpenAI if no key)."""
        self.logger = logger

        # Defer OpenAI initialization until we know key exists
        api_key = get_config_value("OPENAI_API_KEY")
        base_url = get_config_value("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self._llm_ready = bool(api_key)

        openai_client = None
        if self._llm_ready:
            openai_client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=60.0,
            )
            self.logger.info(" OPENAI_API_KEY configured; LLM-driven planner/extractor ready")
        else:
            self.logger.warning(" OPENAI_API_KEY not set; agent will defer to request time")

        # Initialize pipeline stages
        api = MycoPortalAPI()  # Create MycoPortal API client
        self.planner = MycoPortalPlanner(openai_client) if self._llm_ready else None
        self.extractor = MycoPortalExtractor(openai_client) if self._llm_ready else None
        self.resolver = MycoPortalResolver()
        self.router = MycoPortalRouter()
        self.executor = MycoPortalExecutor(api)

    @override
    def get_agent_card(self) -> AgentCard:
        """Return agent metadata for ichatbio platform."""
        return AgentCard(
            name="MycoPortal Fungal Biodiversity Agent",
            description="Search and analyze fungal biodiversity data from MycoPortal (Symbiota network)",
            icon="https://www.mycoportal.org/portal/images/logo.png",
            url="http://localhost:9998",
            entrypoints=[
                AgentEntrypoint(
                    id="search_fungi",
                    description="Search MycoPortal for fungal records, species information, and distributions",
                    parameters=MycoPortalParams
                )
            ]
        )

    @override
    async def run(
        self,
        context: ResponseContext,
        request: str,
        entrypoint: str,
        params: MycoPortalParams,
    ) -> None:
        """Execute five-stage pipeline: Plan → Extract → Resolve → Route → Execute."""
        try:
            if not self._llm_ready or self.planner is None or self.extractor is None:
                await context.reply(
                    "Configuration error: OPENAI_API_KEY is missing. "
                    "Set OPENAI_API_KEY in environment or env.yaml, then restart the server."
                )
                return

            query = request
            self.logger.info(f"Query: {query}")

            # Stage 1: Planner (intent → tool selection)
            plan = await self.planner.plan(query)
            self.logger.info(f"Plan: intent={plan.intent}, tools={plan.tools_planned}")

            # Stage 2: Extractor (query → typed parameters)
            extraction = await self.extractor.extract(query, plan)

            if extraction.clarification_needed:
                await context.reply(extraction.clarification_question)
                return

            self.logger.info(f"Extraction: {extraction}")

            # Stage 3: Resolver (optional identifier enrichment)
            resolution = await self.resolver.resolve(extraction)
            self.logger.info(f"Resolution: {resolution}")

            # Stage 4: Router (extraction → API params)
            routed = self.router.route(plan, extraction, resolution)
            self.logger.info(f"Routed params: {routed}")

            # Stage 5: Executor (API calls + artifact creation)
            await self.executor.execute(context, plan, routed)

        except Exception as e:
            self.logger.exception(f"Pipeline error: {e}")
            await context.reply(f"Error processing request: {str(e)}")


_agent: Optional[MycoPortalAgent] = None


def get_agent() -> MycoPortalAgent:
    """Get or create singleton agent instance."""
    global _agent
    if _agent is None:
        _agent = MycoPortalAgent()
    return _agent
