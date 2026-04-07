from __future__ import annotations

import json
from pathlib import Path

import allure
import pytest

from tests.fixtures.mock_context import FakeResponseContext


DATASET_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "eval_dataset.json"
DATASET = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
FUNCTIONAL_CASES = [
    case for case in DATASET if case.get("run_functional", True) and not case.get("should_fail", False)
]
EXPECTED_FAILURE_CASES = [case for case in DATASET if case.get("should_fail", False)]
CLARIFICATION_CASES = [
    case for case in DATASET if case.get("expected_clarification_needed", False)
]


@pytest.mark.asyncio
@pytest.mark.functional
@pytest.mark.liveapi
@pytest.mark.llm
@pytest.mark.smoke
@pytest.mark.parametrize("case", FUNCTIONAL_CASES, ids=[str(case["id"]) for case in FUNCTIONAL_CASES])
async def test_live_pipeline_generates_artifact_for_case(pipeline: dict[str, object], case: dict[str, object]) -> None:

    planner = pipeline["planner"]
    extractor = pipeline["extractor"]
    resolver = pipeline["resolver"]
    router = pipeline["router"]
    executor = pipeline["executor"]

    query = str(case["query"])
    context = FakeResponseContext()

    plan = await planner.plan(query)
    allure.attach(json.dumps(plan.model_dump(), indent=2), name="planner_output", attachment_type=allure.attachment_type.JSON)
    assert plan.intent == case["expected_intent"]
    assert any(t.tool_name == case["expected_tool"] for t in plan.tools_planned)

    extraction = await extractor.extract(query, plan)
    allure.attach(json.dumps(extraction.model_dump(), indent=2), name="extraction_output", attachment_type=allure.attachment_type.JSON)
    assert not extraction.clarification_needed

    resolution = await resolver.resolve(extraction)
    routed = router.route(plan, extraction, resolution)
    allure.attach(json.dumps({k: v.model_dump(exclude_none=True) for k, v in routed.items()}, indent=2), name="routed_params", attachment_type=allure.attachment_type.JSON)

    await executor.execute(context, plan, routed)

    assert context.artifacts, "Expected at least one artifact to be created"
    artifact = context.artifacts[0]
    assert artifact.description
    assert "MycoPortal" in artifact.description
    assert artifact.metadata.get("data_source") == "MycoPortal"
    assert "retrieval_date" in artifact.metadata
    assert artifact.uris and artifact.uris[0].startswith("http")

    allure.attach(
        json.dumps(
            {
                "description": artifact.description,
                "metadata": artifact.metadata,
                "uri": artifact.uris[0],
                "reply_messages": context.replies,
            },
            indent=2,
        ),
        name="artifact_summary",
        attachment_type=allure.attachment_type.JSON,
    )


@pytest.mark.asyncio
@pytest.mark.functional
@pytest.mark.llm
@pytest.mark.negative
@pytest.mark.parametrize("case", EXPECTED_FAILURE_CASES, ids=[str(case["id"]) for case in EXPECTED_FAILURE_CASES])
async def test_expected_failure_case_mismatches_intent(pipeline: dict[str, object], case: dict[str, object]) -> None:
    planner = pipeline["planner"]

    query = str(case["query"])
    expected_intent = str(case["expected_intent"])

    plan = await planner.plan(query)
    allure.attach(
        json.dumps(
            {
                "query": query,
                "expected_intent": expected_intent,
                "actual_intent": plan.intent,
                "failure_reason": case.get("failure_reason", "intent mismatch expected"),
            },
            indent=2,
        ),
        name="expected_failure_validation",
        attachment_type=allure.attachment_type.JSON,
    )

    with pytest.raises(AssertionError):
        assert plan.intent == expected_intent


@pytest.mark.asyncio
@pytest.mark.functional
@pytest.mark.llm
@pytest.mark.parametrize("case", CLARIFICATION_CASES, ids=[str(case["id"]) for case in CLARIFICATION_CASES])
async def test_clarification_case_requests_followup(pipeline: dict[str, object], case: dict[str, object]) -> None:
    planner = pipeline["planner"]
    extractor = pipeline["extractor"]

    query = str(case["query"])
    plan = await planner.plan(query)
    extraction = await extractor.extract(query, plan)

    allure.attach(
        json.dumps(
            {
                "query": query,
                "planned_intent": plan.intent,
                "clarification_needed": extraction.clarification_needed,
                "clarification_question": extraction.clarification_question,
            },
            indent=2,
        ),
        name="clarification_case",
        attachment_type=allure.attachment_type.JSON,
    )

    assert extraction.clarification_needed is True
    assert extraction.clarification_question
