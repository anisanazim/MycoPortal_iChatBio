from __future__ import annotations

import json
import os
from pathlib import Path

import allure
import pytest
from common.config import get_config_value

try:
    from deepeval.metrics import GEval
    from deepeval.test_case import LLMTestCase, LLMTestCaseParams
except Exception:  # pragma: no cover - handled at runtime in environments missing deepeval
    GEval = None
    LLMTestCase = None
    LLMTestCaseParams = None


DATASET_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "eval_dataset.json"
DATASET = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
QUALITY_CASES = [
    case
    for case in DATASET
    if case.get("run_quality", False)
    and not case.get("should_fail", False)
    and not case.get("expected_clarification_needed", False)
]


def _tool_summary(plan) -> str:
    return "; ".join(
        f"{tool.tool_name} ({tool.priority}): {tool.reason}" for tool in plan.tools_planned
    ) or "No tools planned"


def _build_metric(name: str, criteria: str, threshold: float = 0.75):
    return GEval(
        name=name,
        criteria=criteria,
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=threshold,
        model="gpt-4o-mini",
    )


def _measure_metric(metric, query: str, actual_output: str, expected_output: str) -> tuple[float, str]:
    test_case = LLMTestCase(
        input=query,
        actual_output=actual_output,
        expected_output=expected_output,
    )

    try:
        metric.measure(test_case)
    except Exception as e:  
        error_text = str(e).lower()
        if "invalid_api_key" in error_text or "authentication" in error_text:
            pytest.skip(f"DeepEval authentication unavailable for configured provider: {e}")
        raise

    return float(metric.score), str(getattr(metric, "reason", ""))


@pytest.mark.asyncio
@pytest.mark.quality
@pytest.mark.llm
@pytest.mark.parametrize("case", QUALITY_CASES, ids=[str(case["id"]) for case in QUALITY_CASES])
async def test_reasoning_and_tool_quality_with_deepeval(pipeline: dict[str, object], case: dict[str, object]) -> None:
    if GEval is None or LLMTestCase is None or LLMTestCaseParams is None:
        pytest.skip("DeepEval is not available in the active environment")

    api_key = os.getenv("OPENAI_API_KEY") or get_config_value("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY is required for DeepEval quality tests")
    os.environ["OPENAI_API_KEY"] = api_key

    base_url = os.getenv("OPENAI_BASE_URL") or get_config_value("OPENAI_BASE_URL")
    if base_url:
        os.environ["OPENAI_BASE_URL"] = base_url

    planner = pipeline["planner"]
    extractor = pipeline["extractor"]

    query = str(case["query"])
    expected_intent = str(case["expected_intent"])
    expected_tool = str(case["expected_tool"])

    plan = await planner.plan(query)
    extraction = await extractor.extract(query, plan)
    allure.attach(json.dumps(plan.model_dump(), indent=2), name="planner_output", attachment_type=allure.attachment_type.JSON)

    allure.attach(
        json.dumps(extraction.model_dump(), indent=2),
        name="extraction_output",
        attachment_type=allure.attachment_type.JSON,
    )

    expected_reasoning = (
        f"The reasoning should justify why {expected_tool} is the right tool for this query "
        f"and stay aligned with the {expected_intent} intent."
    )
    
    reasoning_metric = _build_metric(
        name="Reasoning Quality",
        criteria=(
            "Score how well the planner explains why the selected tool is appropriate for the user's query."
        ),
        threshold=0.60,
    )
    reasoning_score, reasoning_reason = _measure_metric(
        reasoning_metric,
        query,
        plan.reasoning,
        expected_reasoning,
    )

    allure.attach(
        json.dumps(
            {
                "query": query,
                "actual_output": plan.reasoning,
                "expected_output": expected_reasoning,
                "score": reasoning_score,
                "threshold": reasoning_metric.threshold,
                "reason": reasoning_reason,
            },
            indent=2,
        ),
        name="deepeval_reasoning_metric",
        attachment_type=allure.attachment_type.JSON,
    )

    tool_metric = _build_metric(
        name="Tool Selection Justification",
        criteria=(
            "Score whether the selected tool and its justification match the user's need."
        ),
        threshold=0.60,
    )
    tool_score, tool_reason = _measure_metric(
        tool_metric,
        query,
        _tool_summary(plan),
        f"The planner should choose {expected_tool} as the must-call tool and justify it clearly.",
    )

    allure.attach(
        json.dumps(
            {
                "query": query,
                "actual_output": _tool_summary(plan),
                "expected_output": f"The planner should choose {expected_tool} as the must-call tool and justify it clearly.",
                "score": tool_score,
                "threshold": tool_metric.threshold,
                "reason": tool_reason,
            },
            indent=2,
        ),
        name="deepeval_tool_metric",
        attachment_type=allure.attachment_type.JSON,
    )

    assert reasoning_score >= reasoning_metric.threshold
    assert tool_score >= tool_metric.threshold
