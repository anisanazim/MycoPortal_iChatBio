from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest
from openai import AsyncOpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from client.api import MycoPortalAPI
from common.config import get_config_value
from execution.executor import MycoPortalExecutor
from extraction.extractor import MycoPortalExtractor
from planning.planner import MycoPortalPlanner
from resolution.resolver import MycoPortalResolver
from routing.router import MycoPortalRouter


@pytest.fixture(scope="session")
def eval_dataset() -> list[dict[str, object]]:
    dataset_path = Path(__file__).parent / "fixtures" / "eval_dataset.json"
    return json.loads(dataset_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def openai_client() -> AsyncOpenAI:
    api_key = get_config_value("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY is required for evaluation tests")

    base_url = get_config_value("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=60.0,
    )


@pytest.fixture(scope="session")
def pipeline(openai_client: AsyncOpenAI) -> dict[str, object]:
    planner = MycoPortalPlanner(openai_client)
    extractor = MycoPortalExtractor(openai_client)
    resolver = MycoPortalResolver()
    router = MycoPortalRouter()
    api = MycoPortalAPI()
    executor = MycoPortalExecutor(api)

    return {
        "planner": planner,
        "extractor": extractor,
        "resolver": resolver,
        "router": router,
        "executor": executor,
    }
