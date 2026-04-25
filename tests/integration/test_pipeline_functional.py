from __future__ import annotations

import json
import os

import allure
import pytest
from pydantic import ValidationError

from tests.fixtures.mock_context import FakeResponseContext
from extraction.models import (
    CollectionListExtraction,
    ExsiccataListExtraction,
    MediaLookupExtraction,
    MorphologyListExtraction,
    OccurrenceByIdExtraction,
    OccurrenceSearchExtraction,
    TaxonByIdExtraction,
    TaxonomySearchExtraction,
)
from tests.data.loader import load_dataset_from_env


VALID_INTENTS = {
    "occurrence_search",
    "occurrence_by_id",
    "taxonomy_search",
    "taxon_by_id",
    "collection_list",
    "media_lookup",
    "morphology_list",
    "exsiccata_list",
    "out_of_scope",
    "unknown",
}

DATASET = load_dataset_from_env()
DATASET_MODE = os.getenv("MYCO_TEST_MODE", "smoke")
DATASET_ENDPOINT = os.getenv("MYCO_TEST_ENDPOINT")
FUNCTIONAL_CASES = [
    case for case in DATASET if case.get("run_functional", True) and not case.get("should_fail", False)
]
EXPECTED_FAILURE_CASES = [case for case in DATASET if case.get("should_fail", False)]
CLARIFICATION_CASES = [
    case for case in DATASET if case.get("expected_clarification_needed", False)
]
VALIDATION_FAILURE_CASES = [
    case for case in DATASET if case.get("should_fail_validation", False)
]


def _set_allure_case_context(case: dict[str, object], bucket: str) -> None:
    case_id = str(case.get("id", "unknown_case"))
    expected_intent = str(case.get("expected_intent", "unknown"))
    category = str(case.get("test_category", bucket))

    allure.dynamic.parent_suite("MycoPortal Evaluation")
    allure.dynamic.suite(f"Dataset Mode: {DATASET_MODE}")
    allure.dynamic.sub_suite("Functional Pipeline")
    allure.dynamic.feature(f"Intent: {expected_intent}")
    allure.dynamic.story(bucket)
    allure.dynamic.title(f"{case_id} [{bucket}] ({DATASET_MODE})")

    allure.dynamic.tag(f"dataset_mode:{DATASET_MODE}")
    allure.dynamic.tag(f"intent:{expected_intent}")
    allure.dynamic.tag(f"category:{category}")
    if DATASET_ENDPOINT:
        allure.dynamic.tag(f"dataset_endpoint:{DATASET_ENDPOINT}")

    allure.attach(
        json.dumps(
            {
                "case_id": case_id,
                "bucket": bucket,
                "dataset_mode": DATASET_MODE,
                "dataset_endpoint": DATASET_ENDPOINT,
                "expected_intent": expected_intent,
                "category": category,
                "query": case.get("query"),
            },
            indent=2,
        ),
        name="test_context",
        attachment_type=allure.attachment_type.JSON,
    )


def _assert_planner_invariants(plan) -> None:
    assert plan.reasoning is not None
    assert plan.reasoning.strip() != ""
    assert all(t.reason and t.reason.strip() != "" for t in plan.tools_planned)

    must_call_tool_names = [t.tool_name for t in plan.tools_planned if t.priority == "must_call"]
    assert len(must_call_tool_names) == len(set(must_call_tool_names))

    if plan.clarification_needed:
        assert plan.clarification_question is not None
        assert plan.clarification_question.strip() != ""

    if plan.intent not in ("out_of_scope", "unknown"):
        assert len(must_call_tool_names) > 0


def _assert_extractor_invariants(extraction, intent: str) -> None:
    assert extraction.clarification_needed is not None

    if extraction.clarification_needed:
        assert extraction.clarification_question is not None
        assert extraction.clarification_question.strip() != ""
        return

    assert extraction.clarification_question is None

    if intent == "occurrence_search":
        assert isinstance(extraction, OccurrenceSearchExtraction)
        assert extraction.limit > 0
        assert extraction.offset >= 0

    elif intent == "occurrence_by_id":
        assert isinstance(extraction, OccurrenceByIdExtraction)
        assert extraction.identifier is not None
        assert extraction.identifier.strip() != ""

    elif intent == "taxonomy_search":
        assert isinstance(extraction, TaxonomySearchExtraction)
        assert extraction.taxon is not None
        assert extraction.taxon.strip() != ""
        assert extraction.search_type in ("EXACT", "START", "WHOLEWORD", "WILD")

    elif intent == "taxon_by_id":
        assert isinstance(extraction, TaxonByIdExtraction)
        assert extraction.identifier is not None
        assert isinstance(extraction.identifier, int)
        assert extraction.identifier > 0

    elif intent == "collection_list":
        assert isinstance(extraction, CollectionListExtraction)
        assert extraction.limit > 0
        assert extraction.offset >= 0

    elif intent == "media_lookup":
        assert isinstance(extraction, MediaLookupExtraction)
        assert extraction.limit > 0
        assert extraction.offset >= 0

    elif intent == "morphology_list":
        assert isinstance(extraction, MorphologyListExtraction)
        assert extraction.include_states in (0, 1)
        assert extraction.limit > 0
        assert extraction.offset >= 0

    elif intent == "exsiccata_list":
        assert isinstance(extraction, ExsiccataListExtraction)
        assert extraction.limit > 0
        assert extraction.offset >= 0


@pytest.mark.asyncio
@pytest.mark.functional
@pytest.mark.liveapi
@pytest.mark.llm
@pytest.mark.smoke
@pytest.mark.parametrize("case", FUNCTIONAL_CASES, ids=[str(case["id"]) for case in FUNCTIONAL_CASES])
async def test_live_pipeline_generates_artifact_for_case(pipeline: dict[str, object], case: dict[str, object]) -> None:
    _set_allure_case_context(case, "functional_success")

    planner = pipeline["planner"]
    extractor = pipeline["extractor"]
    resolver = pipeline["resolver"]
    router = pipeline["router"]
    executor = pipeline["executor"]

    query = str(case["query"])
    context = FakeResponseContext()

    plan = await planner.plan(query)
    _assert_planner_invariants(plan)
    allure.attach(json.dumps(plan.model_dump(), indent=2), name="planner_output", attachment_type=allure.attachment_type.JSON)
    assert plan.intent == case["expected_intent"]
    assert plan.intent in VALID_INTENTS

    must_call_tools = [t.tool_name for t in plan.tools_planned if t.priority == "must_call"]
    assert case["expected_tool"] in must_call_tools
    assert len(must_call_tools) == 1

    extraction = await extractor.extract(query, plan)
    _assert_extractor_invariants(extraction, plan.intent)
    allure.attach(json.dumps(extraction.model_dump(), indent=2), name="extraction_output", attachment_type=allure.attachment_type.JSON)
    assert not extraction.clarification_needed

    expected_search_type = case.get("expected_search_type")
    if expected_search_type and plan.intent == "taxonomy_search":
        assert isinstance(extraction, TaxonomySearchExtraction)
        assert extraction.search_type == expected_search_type

    resolution = await resolver.resolve(extraction)
    routed = router.route(plan, extraction, resolution)
    allure.attach(json.dumps({k: v.model_dump(exclude_none=True) for k, v in routed.items()}, indent=2), name="routed_params", attachment_type=allure.attachment_type.JSON)

    if expected_search_type and "search_taxonomy" in routed:
        assert routed["search_taxonomy"].type == expected_search_type

    planned_tools = {t.tool_name for t in plan.tools_planned if t.priority == "must_call"}
    routed_tools = set(routed.keys())
    assert planned_tools.issubset(routed_tools)

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
    _set_allure_case_context(case, "expected_failure")

    planner = pipeline["planner"]

    query = str(case["query"])
    expected_intent = str(case["expected_intent"])

    plan = await planner.plan(query)
    _assert_planner_invariants(plan)
    assert plan.intent in VALID_INTENTS
    assert plan.intent != expected_intent
    
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


@pytest.mark.asyncio
@pytest.mark.functional
@pytest.mark.llm
@pytest.mark.parametrize("case", CLARIFICATION_CASES, ids=[str(case["id"]) for case in CLARIFICATION_CASES])
async def test_clarification_case_requests_followup(pipeline: dict[str, object], case: dict[str, object]) -> None:
    _set_allure_case_context(case, "clarification")

    planner = pipeline["planner"]
    extractor = pipeline["extractor"]

    query = str(case["query"])
    expected_stage = str(case.get("clarification_stage", "extractor")).strip().lower()

    plan = await planner.plan(query)
    _assert_planner_invariants(plan)

    if expected_stage not in {"planner", "extractor", "any"}:
        raise ValueError(f"Unsupported clarification_stage '{expected_stage}'")

    if expected_stage == "planner":
        allure.attach(
            json.dumps(
                {
                    "query": query,
                    "expected_stage": expected_stage,
                    "planned_intent": plan.intent,
                    "planner_clarification_needed": plan.clarification_needed,
                    "planner_clarification_question": plan.clarification_question,
                },
                indent=2,
            ),
            name="clarification_case",
            attachment_type=allure.attachment_type.JSON,
        )
        assert plan.clarification_needed is True
        assert plan.clarification_question
        return

    if expected_stage == "any" and plan.clarification_needed:
        allure.attach(
            json.dumps(
                {
                    "query": query,
                    "expected_stage": expected_stage,
                    "planned_intent": plan.intent,
                    "clarification_source": "planner",
                    "clarification_needed": plan.clarification_needed,
                    "clarification_question": plan.clarification_question,
                },
                indent=2,
            ),
            name="clarification_case",
            attachment_type=allure.attachment_type.JSON,
        )
        assert plan.clarification_question
        return

    extraction = await extractor.extract(query, plan)
    _assert_extractor_invariants(extraction, plan.intent)

    allure.attach(
        json.dumps(
            {
                "query": query,
                "expected_stage": expected_stage,
                "planned_intent": plan.intent,
                "clarification_source": "extractor",
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


@pytest.mark.asyncio
@pytest.mark.functional
@pytest.mark.llm
@pytest.mark.parametrize("case", VALIDATION_FAILURE_CASES, ids=[str(case["id"]) for case in VALIDATION_FAILURE_CASES])
async def test_validation_failure_detected(pipeline: dict[str, object], case: dict[str, object]) -> None:
    """Data-driven test: verify validation failures are caught at expected assertion points"""
    _set_allure_case_context(case, "validation_failure")
    
    planner = pipeline["planner"]
    extractor = pipeline["extractor"]
    resolver = pipeline["resolver"]
    router = pipeline["router"]

    query = str(case["query"])
    expected_intent = str(case["expected_intent"])
    expected_tool = str(case["expected_tool"])
    validation_failure_point = str(case.get("validation_failure_point", "unknown"))

    plan = await planner.plan(query)
    _assert_planner_invariants(plan)

    # Log what we got for debugging
    allure.attach(
        json.dumps(
            {
                "query": query,
                "expected_intent": expected_intent,
                "expected_tool": expected_tool,
                "actual_intent": plan.intent,
                "actual_tools": [t.tool_name for t in plan.tools_planned if t.priority == "must_call"],
                "validation_failure_point": validation_failure_point,
            },
            indent=2,
        ),
        name="validation_case_context",
        attachment_type=allure.attachment_type.JSON,
    )

    if validation_failure_point == "intent_mismatch":
        # Should fail when plan intent doesn't match expected
        with pytest.raises(AssertionError, match="expected_intent"):
            assert plan.intent == expected_intent, f"Intent mismatch: {plan.intent} != {expected_intent}"

    elif validation_failure_point == "must_call_tools_mismatch":
        # Should fail when expected_tool not in must_call tools
        must_call_tools = [t.tool_name for t in plan.tools_planned if t.priority == "must_call"]
        with pytest.raises(AssertionError):
            assert expected_tool in must_call_tools, f"Tool {expected_tool} not in {must_call_tools}"

    elif validation_failure_point == "routed_tools_mismatch":
        # Extract and route, then check if planned tools are in routed
        extraction = await extractor.extract(query, plan)
        _assert_extractor_invariants(extraction, plan.intent)
        
        resolution = await resolver.resolve(extraction)
        routed = router.route(plan, extraction, resolution)
        
        planned_tools = {t.tool_name for t in plan.tools_planned if t.priority == "must_call"}
        routed_tools = set(routed.keys())
        
        with pytest.raises(AssertionError):
            assert planned_tools.issubset(routed_tools), f"Planned {planned_tools} not subset of routed {routed_tools}"

    elif validation_failure_point == "param_schema_validation":
        extraction = await extractor.extract(query, plan)
        _assert_extractor_invariants(extraction, plan.intent)

        resolution = await resolver.resolve(extraction)
        with pytest.raises(ValidationError):
            router.route(plan, extraction, resolution)

    allure.attach(
        json.dumps(
            {
                "validation_failure_point": validation_failure_point,
                "failure_reason": case.get("failure_reason", "Unknown"),
                "status": "validation failure detected as expected",
            },
            indent=2,
        ),
        name="validation_result",
        attachment_type=allure.attachment_type.JSON,
    )