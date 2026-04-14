from __future__ import annotations

import logging

import instructor
from instructor.exceptions import InstructorRetryException
from openai import AsyncOpenAI

from extraction.models import (
    CollectionListExtraction,
    ExtractionResult,
    MediaLookupExtraction,
    OccurrenceByIdExtraction,
    OccurrenceSearchExtraction,
    TaxonByIdExtraction,
    TaxonomySearchExtraction,
)
from planning.models import PlannerOutput

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
- For occurrence_search, any single valid filter is enough to run search (species, catalog number,
  family, recordedBy, recordedByLastName, eventDate, county, stateProvince, or country).
- Do not set clarification_needed for occurrence_search when at least one valid filter is present.

## ID RULES

- occurrence_by_id requires identifier (string)
- For occurrence_by_id, if identifier is not in UUID format (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx),
  set clarification_needed=True and ask user to provide UUID with hyphens.
- For malformed catalog numbers (not like DBG-F-010127), set clarification_needed=True and suggest a corrected dashed format.
- taxon_by_id requires identifier (integer tid)
- media_lookup may include tid (integer) if present

## TAXON RULES

- taxonomy_search requires taxon term
- taxonomy_search search_type mapping:
    - Use START for phrases like "start with", "starting with", "begins with", "prefix"
    - Use WHOLEWORD for phrases like "whole word", "exact word", "word <term>"
    - Use WILD for contains/pattern phrasing such as "contains", "include", "anything with",
        "in the name", "matching pattern", or when wildcard characters like * or ? appear
    - Use EXACT only for direct lookup/classification phrasing without prefix/wholeword/wildcard hints
- Do not default taxonomy_search search_type to EXACT when query wording implies START, WHOLEWORD, or WILD
- Keep taxon/species terms exactly as user wrote them unless normalization is required
- occurrence_search uses binomen-only scientific names, catalog numbers, collector names, and location/date filters
- occurrence_search catalog numbers look like DBG-F-010127
- occurrence_search event dates must be YYYY, YYYY-MM, or YYYY-MM-DD
- occurrence_search county must be a single county name

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