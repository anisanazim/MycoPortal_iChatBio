from __future__ import annotations

import os
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
from tests.data.loader import load_dataset


def pytest_addoption(parser):
    parser.addoption(
        "--dataset-mode",
        action="store",
        default=None,
        choices=["smoke", "endpoint", "regression"],
        help="Dataset mode: smoke (eval_dataset), endpoint (single endpoint file), regression (all endpoint files)",
    )
    parser.addoption(
        "--endpoint",
        action="store",
        default=None,
        help="Endpoint name for --dataset-mode=endpoint (e.g. taxonomy_search)",
    )


def pytest_configure(config):
    dataset_mode = config.getoption("dataset_mode")
    endpoint = config.getoption("endpoint")

    if dataset_mode:
        os.environ["MYCO_TEST_MODE"] = dataset_mode
    if endpoint:
        os.environ["MYCO_TEST_ENDPOINT"] = endpoint


@pytest.fixture(scope="session")
def eval_dataset() -> list[dict[str, object]]:
    mode = os.getenv("MYCO_TEST_MODE", "smoke")
    endpoint = os.getenv("MYCO_TEST_ENDPOINT")
    return load_dataset(mode=mode, endpoint=endpoint)


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
