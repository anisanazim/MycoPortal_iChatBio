from __future__ import annotations

import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
SMOKE_FILE = DATA_DIR / "eval_dataset.json"

# Intent/endpoint name -> API-specific test data file
ENDPOINT_FILE_MAP: dict[str, str] = {
    "occurrence_search": "occurrence_search_testdata.json",
    "occurrence_by_id": "occurrence_by_id_testdata.json",
    "taxonomy_search": "taxonomy_search_testdata.json",
    "taxon_by_id": "taxon_by_id_testdata.json",
    "collection_list": "collection_list_testdata.json",
    "media_lookup": "media_lookup_testdata.json",
}


def _read_json(path: Path) -> list[dict[str, object]]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_smoke_dataset() -> list[dict[str, object]]:
    """Load smoke dataset (single consolidated file)."""
    return _read_json(SMOKE_FILE)


def load_endpoint_dataset(endpoint: str) -> list[dict[str, object]]:
    """Load dataset for one endpoint/intent."""
    file_name = ENDPOINT_FILE_MAP.get(endpoint)
    if not file_name:
        valid = ", ".join(sorted(ENDPOINT_FILE_MAP.keys()))
        raise ValueError(f"Unknown endpoint '{endpoint}'. Valid values: {valid}")
    return _read_json(DATA_DIR / file_name)


def load_regression_dataset() -> list[dict[str, object]]:
    """Load all API-specific endpoint datasets (excludes smoke eval_dataset)."""
    all_cases: list[dict[str, object]] = []
    seen_ids: set[str] = set()

    for endpoint in sorted(ENDPOINT_FILE_MAP.keys()):
        cases = load_endpoint_dataset(endpoint)
        for case in cases:
            case_id = str(case.get("id", ""))
            if case_id and case_id in seen_ids:
                continue
            if case_id:
                seen_ids.add(case_id)
            all_cases.append(case)

    return all_cases


def load_dataset(mode: str = "smoke", endpoint: str | None = None) -> list[dict[str, object]]:
    """
    Mode options:
    - smoke: consolidated eval dataset
    - endpoint: single endpoint dataset (requires endpoint)
    - regression: combined API-specific endpoint datasets
    """
    normalized_mode = (mode or "smoke").strip().lower()

    if normalized_mode == "smoke":
        return load_smoke_dataset()

    if normalized_mode == "endpoint":
        if not endpoint:
            raise ValueError("Endpoint mode requires endpoint name")
        return load_endpoint_dataset(endpoint.strip())

    if normalized_mode == "regression":
        return load_regression_dataset()

    raise ValueError("Invalid mode. Use one of: smoke, endpoint, regression")


def load_dataset_from_env() -> list[dict[str, object]]:
    """Read dataset mode config from environment variables."""
    mode = os.getenv("MYCO_TEST_MODE", "smoke")
    endpoint = os.getenv("MYCO_TEST_ENDPOINT")
    return load_dataset(mode=mode, endpoint=endpoint)
