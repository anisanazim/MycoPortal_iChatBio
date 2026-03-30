from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class OccurrenceSearchParams(BaseModel):
    collid: Optional[str] = Field(default=None)
    sciname: Optional[str] = Field(default=None)
    family: Optional[str] = Field(default=None)
    recordedBy: Optional[str] = Field(default=None)
    eventDate: Optional[str] = Field(default=None, description="YYYY, YYYY-MM, or YYYY-MM-DD")
    country: Optional[str] = Field(default=None)
    stateProvince: Optional[str] = Field(default=None)
    county: Optional[str] = Field(default=None)
    datasetID: Optional[str] = Field(default=None)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class OccurrenceByIdParams(BaseModel):
    identifier: str = Field(..., min_length=1)
    includeMedia: Optional[int] = Field(default=None)
    includeIdentifications: Optional[int] = Field(default=None)


class TaxonomySearchParams(BaseModel):
    taxon: str = Field(..., min_length=1)
    type: Literal["EXACT", "START", "WHOLEWORD", "WILD"] = Field(default="EXACT")
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class TaxonByIdParams(BaseModel):
    identifier: int = Field(..., ge=1)


class CollectionListParams(BaseModel):
    managementType: Optional[Literal["live", "snapshot", "aggregate"]] = Field(default=None)
    collectionType: Optional[Literal["preservedSpecimens", "observations", "researchObservation"]] = Field(default=None)
    limit: int = Field(default=1000, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class MediaLookupParams(BaseModel):
    tid: Optional[int] = Field(default=None, ge=1)
    includeSynonyms: int = Field(default=0, ge=0, le=1)
    includeChildren: int = Field(default=0, ge=0, le=1)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
