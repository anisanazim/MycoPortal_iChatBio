from __future__ import annotations

from mycoportal_agent.extraction.models import ExtractionResult
from mycoportal_agent.resolution.models import ResolutionResult


class MycoPortalResolver:
    """Resolver stage placeholder for MycoPortal normalization/clarification."""

    async def resolve(self, extraction: ExtractionResult) -> ResolutionResult:
        # v1 performs lightweight validation through extractor and models.
        # Keep stage for future synonym/identifier enrichment logic.
        return ResolutionResult()
