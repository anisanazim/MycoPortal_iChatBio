from __future__ import annotations

import json
from datetime import datetime


def _extract_payload_count(payload: dict) -> int | None:
    for key in ("count", "total", "totalRecords", "total_records"):
        value = payload.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def _extract_returned_count(payload: dict) -> int | None:
    for key in ("results", "records", "occurrences", "data", "items"):
        value = payload.get(key)
        if isinstance(value, list):
            return len(value)
    return None


def _extract_title(payload: dict) -> str | None:
    for key in (
        "scientificName",
        "taxonName",
        "name",
        "title",
        "displayName",
        "label",
    ):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def build_artifact_description(base: str, request_summary: str | None = None, payload: dict | None = None) -> str:
    description = base
    if request_summary:
        description = f"{description} for {request_summary}"

    if payload:
        title = _extract_title(payload)
        if title:
            description = f"{description}: {title}"

        total = _extract_payload_count(payload)
        returned = _extract_returned_count(payload)
        stats: list[str] = []
        if total is not None:
            stats.append(f"{total:,} total")
        if returned is not None and returned != total:
            stats.append(f"{returned:,} returned")
        if stats:
            description = f"{description} ({'; '.join(stats)})"

    return description


async def create_json_artifact(process, description: str, url: str, payload: dict, metadata: dict | None = None) -> None:
    info = metadata or {}
    info.setdefault("data_source", "MycoPortal")
    info.setdefault("retrieval_date", datetime.now().strftime("%Y-%m-%d"))

    await process.create_artifact(
        mimetype="application/json",
        description=description,
        uris=[url],
        content=json.dumps(payload).encode("utf-8"),
        metadata=info,
    )
