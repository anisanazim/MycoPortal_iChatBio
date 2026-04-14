from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


class ExtractionBase(BaseModel):
    clarification_needed: bool = Field(default=False)
    clarification_question: Optional[str] = Field(default=None)


class OccurrenceSearchExtraction(ExtractionBase):
    species: Optional[str] = None
    state_province: Optional[str] = None
    county: Optional[str] = None
    country: Optional[str] = None
    family: Optional[str] = None
    catalog_number: Optional[str] = None
    recorded_by: Optional[str] = None
    recorded_by_last_name: Optional[str] = None
    event_date: Optional[str] = None
    limit: int = 100
    offset: int = 0


class OccurrenceByIdExtraction(ExtractionBase):
    identifier: Optional[str] = None


class TaxonomySearchExtraction(ExtractionBase):
    taxon: Optional[str] = None
    search_type: Literal["EXACT", "START", "WHOLEWORD", "WILD"] = "EXACT"
    limit: int = 100
    offset: int = 0


class TaxonByIdExtraction(ExtractionBase):
    identifier: Optional[int] = None


class CollectionListExtraction(ExtractionBase):
    management_type: Optional[Literal["live", "snapshot", "aggregate"]] = None
    collection_type: Optional[Literal["preservedSpecimens", "observations", "researchObservation"]] = None
    limit: int = 1000
    offset: int = 0


class MediaLookupExtraction(ExtractionBase):
    tid: Optional[int] = None
    include_synonyms: int = 0
    include_children: int = 0
    limit: int = 100
    offset: int = 0


ExtractionResult = Union[
    OccurrenceSearchExtraction,
    OccurrenceByIdExtraction,
    TaxonomySearchExtraction,
    TaxonByIdExtraction,
    CollectionListExtraction,
    MediaLookupExtraction,
]
