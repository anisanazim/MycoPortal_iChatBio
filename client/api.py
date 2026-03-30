from __future__ import annotations

import asyncio
from typing import Any, Optional
from urllib.parse import urlencode

import requests

from common.config import get_config_value
from mycoportal_agent.models.params import (
    CollectionListParams,
    MediaLookupParams,
    OccurrenceByIdParams,
    OccurrenceSearchParams,
    TaxonByIdParams,
    TaxonomySearchParams,
)


class MycoPortalAPI:
    """HTTP wrapper for MycoPortal (Symbiota) read-only v2 endpoints."""

    def __init__(self):
        base_url = get_config_value("MYCOPORTAL_API_BASE_URL", "https://mycoportal.org/portal")
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "MycoPortalAgent/1.0",
        })
        self.timeout_seconds = int(get_config_value("MYCOPORTAL_HTTP_TIMEOUT", "30"))

    def _build_url(self, path: str, query: Optional[dict[str, Any]] = None) -> str:
        q = query or {}
        q = {k: v for k, v in q.items() if v is not None}
        if not q:
            return f"{self.base_url}{path}"
        return f"{self.base_url}{path}?{urlencode(q, doseq=True)}"

    def _execute_get(self, url: str) -> dict[str, Any]:
        try:
            response = self.session.get(url, timeout=self.timeout_seconds)
            response.raise_for_status()
            if not response.text or not response.text.strip():
                return {}
            return response.json()
        except requests.exceptions.Timeout as e:
            raise ConnectionError(f"MycoPortal request timed out: {e}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"MycoPortal request failed: {e}")
        except ValueError as e:
            raise ConnectionError(f"MycoPortal returned non-JSON content: {e}")

    async def get_json(self, url: str) -> dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._execute_get(url))

    def build_occurrence_search_url(self, params: OccurrenceSearchParams) -> str:
        query = params.model_dump(exclude_none=True)
        return self._build_url("/api/v2/occurrence/search", query)

    def build_occurrence_by_id_url(self, params: OccurrenceByIdParams) -> str:
        path = f"/api/v2/occurrence/{params.identifier}"
        query = {
            "includeMedia": params.includeMedia,
            "includeIdentifications": params.includeIdentifications,
        }
        return self._build_url(path, query)

    def build_taxonomy_search_url(self, params: TaxonomySearchParams) -> str:
        return self._build_url("/api/v2/taxonomy/search", params.model_dump(exclude_none=True))

    def build_taxon_by_id_url(self, params: TaxonByIdParams) -> str:
        return self._build_url(f"/api/v2/taxonomy/{params.identifier}")

    def build_collection_list_url(self, params: CollectionListParams) -> str:
        return self._build_url("/api/v2/collection", params.model_dump(exclude_none=True))

    def build_media_lookup_url(self, params: MediaLookupParams) -> str:
        return self._build_url("/api/v2/media", params.model_dump(exclude_none=True))
