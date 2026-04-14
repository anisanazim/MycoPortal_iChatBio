from __future__ import annotations

from extraction.models import (
    CollectionListExtraction,
    ExtractionResult,
    MediaLookupExtraction,
    OccurrenceByIdExtraction,
    OccurrenceSearchExtraction,
    TaxonByIdExtraction,
    TaxonomySearchExtraction,
)
from models.params import (
    CollectionListParams,
    MediaLookupParams,
    OccurrenceByIdParams,
    OccurrenceSearchParams,
    TaxonByIdParams,
    TaxonomySearchParams,
)
from planning.models import PlannerOutput
from resolution.models import ResolutionResult


class MycoPortalRouter:
    """Convert typed extraction into typed MycoPortal API params."""

    def route(
        self,
        plan: PlannerOutput,
        extraction: ExtractionResult,
        resolution: ResolutionResult | None = None,
    ) -> dict[str, object]:
        _ = resolution

        if plan.intent == "occurrence_search":
            e = self._expect(extraction, OccurrenceSearchExtraction)
            return {
                "search_occurrences": OccurrenceSearchParams(
                    collid=None,
                    sciname=e.species,
                    catalogNumber=e.catalog_number,
                    stateProvince=e.state_province,
                    county=e.county,
                    country=e.country,
                    family=e.family,
                    recordedBy=e.recorded_by,
                    recordedByLastName=e.recorded_by_last_name,
                    eventDate=e.event_date,
                    limit=e.limit,
                    offset=e.offset,
                )
            }

        if plan.intent == "occurrence_by_id":
            e = self._expect(extraction, OccurrenceByIdExtraction)
            if not e.identifier:
                raise ValueError("Occurrence identifier is required")
            return {"get_occurrence_by_id": OccurrenceByIdParams(identifier=e.identifier)}

        if plan.intent == "taxonomy_search":
            e = self._expect(extraction, TaxonomySearchExtraction)
            if not e.taxon:
                raise ValueError("Taxon is required for taxonomy search")
            search_type = (e.search_type or "EXACT").upper()
            return {
                "search_taxonomy": TaxonomySearchParams(
                    taxon=e.taxon,
                    type=search_type,
                    limit=e.limit,
                    offset=e.offset,
                )
            }

        if plan.intent == "taxon_by_id":
            e = self._expect(extraction, TaxonByIdExtraction)
            if not e.identifier:
                raise ValueError("Taxon identifier is required")
            return {"get_taxon_by_id": TaxonByIdParams(identifier=e.identifier)}

        if plan.intent == "collection_list":
            e = self._expect(extraction, CollectionListExtraction)
            # Normalize to API-expected values (case-sensitive)
            management_type = e.management_type.lower() if e.management_type else None
            collection_type = e.collection_type if e.collection_type else None
            return {
                "list_collections": CollectionListParams(
                    managementType=management_type,
                    collectionType=collection_type,
                    limit=e.limit,
                    offset=e.offset,
                )
            }

        if plan.intent == "media_lookup":
            e = self._expect(extraction, MediaLookupExtraction)
            return {
                "lookup_media": MediaLookupParams(
                    tid=e.tid,
                    includeSynonyms=e.include_synonyms,
                    includeChildren=e.include_children,
                    limit=e.limit,
                    offset=e.offset,
                )
            }

        return {}

    def _expect(self, extraction: ExtractionResult, expected_type):
        if not isinstance(extraction, expected_type):
            raise ValueError(f"Expected extraction type {expected_type.__name__}")
        return extraction
