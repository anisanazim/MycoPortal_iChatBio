from __future__ import annotations

import re
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field
from pydantic import field_validator


UUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
BINOMEN_PATTERN = r"^[A-Z][A-Za-z-]* [a-z][a-z-]*$"
CATALOG_NUMBER_PATTERN = r"^[A-Z0-9]+(?:-[A-Z0-9]+)+$"


def _normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = " ".join(value.split())
    return normalized or None


class OccurrenceSearchParams(BaseModel):
    collid: Optional[str] = Field(default=None, description="Portal collection identifier")
    sciname: Optional[str] = Field(default=None, description="Binomen only without authorship")
    family: Optional[str] = Field(default=None)
    catalogNumber: Optional[str] = Field(default=None, description="Catalog number such as DBG-F-010127")
    recordedBy: Optional[str] = Field(default=None)
    recordedByLastName: Optional[str] = Field(default=None)
    eventDate: Optional[str] = Field(default=None, description="YYYY, YYYY-MM, or YYYY-MM-DD")
    country: Optional[str] = Field(default=None)
    stateProvince: Optional[str] = Field(default=None)
    county: Optional[str] = Field(default=None)
    datasetID: Optional[str] = Field(default=None)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

    @field_validator(
        "collid",
        "family",
        "recordedBy",
        "recordedByLastName",
        "country",
        "stateProvince",
        "county",
        "datasetID",
        mode="before",
    )
    @classmethod
    def _normalize_text_fields(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)

    @field_validator("sciname", mode="before")
    @classmethod
    def _normalize_sciname(cls, value: Optional[str]) -> Optional[str]:
        normalized = _normalize_optional_text(value)
        if normalized is None:
            return None
        if not re.fullmatch(BINOMEN_PATTERN, normalized):
            raise ValueError("Scientific name must be a binomen in 'Genus species' format")
        return normalized

    @field_validator("catalogNumber", mode="before")
    @classmethod
    def _validate_catalog_number(cls, value: Optional[str]) -> Optional[str]:
        normalized = _normalize_optional_text(value)
        if normalized is None:
            return None
        if not re.fullmatch(CATALOG_NUMBER_PATTERN, normalized):
            raise ValueError("catalogNumber must match the portal catalog format, e.g. DBG-F-010127")
        return normalized

    @field_validator("eventDate", mode="before")
    @classmethod
    def _validate_event_date(cls, value: Optional[str]) -> Optional[str]:
        normalized = _normalize_optional_text(value)
        if normalized is None:
            return None

        if re.fullmatch(r"\d{4}", normalized):
            return normalized

        if re.fullmatch(r"\d{4}-\d{2}", normalized):
            datetime.strptime(normalized, "%Y-%m")
            return normalized

        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized):
            datetime.strptime(normalized, "%Y-%m-%d")
            return normalized

        raise ValueError("eventDate must be YYYY, YYYY-MM, or YYYY-MM-DD")

    @field_validator("county", mode="before")
    @classmethod
    def _validate_county(cls, value: Optional[str]) -> Optional[str]:
        normalized = _normalize_optional_text(value)
        if normalized is None:
            return None
        if "," in normalized:
            raise ValueError("county must be a single county name")
        return normalized


class OccurrenceByIdParams(BaseModel):
    identifier: str = Field(
        ...,
        pattern=UUID_PATTERN,
        description="Occurrence identifier in canonical UUID format",
    )
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


class MorphologyListParams(BaseModel):
    includeStates: int = Field(default=0, ge=0, le=1)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ExsiccataListParams(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
