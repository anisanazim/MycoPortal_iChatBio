from __future__ import annotations

import logging

import instructor
from instructor.exceptions import InstructorRetryException
from openai import AsyncOpenAI

from mycoportal_agent.extraction.models import (
    CollectionListExtraction,
    ExtractionResult,
    MediaLookupExtraction,
    OccurrenceByIdExtraction,
    OccurrenceSearchExtraction,
    TaxonByIdExtraction,
    TaxonomySearchExtraction,
)
from mycoportal_agent.planning.models import PlannerOutput

logger = logging.getLogger(__name__)


INTENT_SCHEMA_MAP: dict[str, type] = {
    "occurrence_search": OccurrenceSearchExtraction,
    "occurrence_by_id": OccurrenceByIdExtraction,
    "taxonomy_search": TaxonomySearchExtraction,
    "taxon_by_id": TaxonByIdExtraction,
    "collection_list": CollectionListExtraction,
    "media_lookup": MediaLookupExtraction,
}


EXTRACTOR_SYSTEM_PROMPT = """
You are a schema-guided parameter extractor for the MycoPortal (Symbiota) API.

The planner has already determined the user's intent: {intent}
Extract only parameters required by the given schema.

## RULES

- Populate only fields defined in the schema
- Do not invent fields or values
- If a required identifier/search term is missing, set clarification_needed=True
- If clarification_needed=True, provide a specific clarification_question

## ID RULES

- occurrence_by_id requires identifier (string)
- taxon_by_id requires identifier (integer tid)
- media_lookup may include tid (integer) if present

## TAXON RULES

- taxonomy_search requires taxon term
- Keep taxon/species terms exactly as user wrote them

## READ-ONLY

- This extractor supports only read-only intents already selected by the planner
"""


class MycoPortalExtractor:
    """LLM-driven parameter extractor for MycoPortal intents."""

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = instructor.from_openai(openai_client)

    async def extract(self, query: str, plan: PlannerOutput) -> ExtractionResult:
        intent = plan.intent
        if intent in ("unknown", "out_of_scope"):
            raise ValueError(f"Intent '{intent}' does not require parameter extraction")

        schema = INTENT_SCHEMA_MAP.get(intent)
        if not schema:
            raise ValueError(f"No extraction schema available for intent '{intent}'")

        system_prompt = EXTRACTOR_SYSTEM_PROMPT.format(intent=intent)
        logger.warning("[MYCO-EXTRACTOR] Extracting for intent: %s", intent)

        try:
            result = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                response_model=schema,
                temperature=0,
                max_retries=2,
            )
        except InstructorRetryException as e:
            logger.error("[MYCO-EXTRACTOR] Failed after retries for intent '%s': %s", intent, e)
            raise

        logger.warning("[MYCO-EXTRACTOR] Result: %s", result.model_dump(exclude_none=True))
        return result
