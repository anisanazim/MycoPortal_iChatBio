from __future__ import annotations

import importlib
import io
import json
import os
from pathlib import Path

import allure
import pytest
from common.config import get_config_value
from tests.data.loader import load_dataset_from_env

try:
    from deepeval.metrics import GEval
    from deepeval.test_case import LLMTestCase, LLMTestCaseParams
except Exception: 
    GEval = None
    LLMTestCase = None
    LLMTestCaseParams = None


DATASET = load_dataset_from_env()
DATASET_MODE = os.getenv("MYCO_TEST_MODE", "smoke")
DATASET_ENDPOINT = os.getenv("MYCO_TEST_ENDPOINT")
REASONING_THRESHOLD = float(os.getenv("MYCO_REASONING_THRESHOLD", "0.75"))
EXTRACTION_THRESHOLD = float(os.getenv("MYCO_EXTRACTION_THRESHOLD", "0.75"))
QUALITY_CASES = [
    case
    for case in DATASET
    if case.get("run_quality", False)
    and not case.get("should_fail", False)
    and not case.get("expected_clarification_needed", False)
]

_QUALITY_SCORE_BUCKETS: dict[str, list[dict[str, object]]] = {
    "quality_reasoning": [],
    "quality_extraction": [],
}
HISTOGRAM_BIN_COUNT = 20
ALLURE_PLOTS_DIR = Path("allure-results") / "plots"


def _save_histogram_png(metric_bucket: str, png_bytes: bytes) -> Path:
    ALLURE_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{DATASET_MODE}_{metric_bucket}_score_distribution.png"
    output_path = ALLURE_PLOTS_DIR / filename
    output_path.write_bytes(png_bytes)
    return output_path


def _attach_score_distribution(metric_bucket: str, threshold: float) -> None:
    records = _QUALITY_SCORE_BUCKETS[metric_bucket]
    if not records:
        return

    scores = [float(item["score"]) for item in records]

    np_mod = None
    try:
        np_mod = importlib.import_module("numpy")
    except ModuleNotFoundError:
        np_mod = None

    if np_mod is not None:
        np_scores = np_mod.array(scores, dtype=float)
        bins = np_mod.linspace(0.0, 1.0, HISTOGRAM_BIN_COUNT + 1)
        np_counts, np_edges = np_mod.histogram(np_scores, bins=bins)
        counts = [int(x) for x in np_counts]
        edges = [float(x) for x in np_edges]
    else:
        edges = [i / float(HISTOGRAM_BIN_COUNT) for i in range(HISTOGRAM_BIN_COUNT + 1)]
        counts = [0 for _ in range(HISTOGRAM_BIN_COUNT)]
        for score in scores:
            clamped = max(0.0, min(1.0, float(score)))
            idx = min(int(clamped * HISTOGRAM_BIN_COUNT), HISTOGRAM_BIN_COUNT - 1)
            counts[idx] += 1

    passed = sum(1 for score in scores if score >= threshold)
    failed = len(scores) - passed

    histogram_payload = {
        "metric_bucket": metric_bucket,
        "threshold": threshold,
        "total_cases": len(scores),
        "pass_count": passed,
        "fail_count": failed,
        "scores": [float(x) for x in scores],
        "bin_edges": edges,
        "bin_counts": counts,
        "cases": records,
    }

    allure.attach(
        json.dumps(histogram_payload, indent=2),
        name=f"deepeval_{metric_bucket}_score_distribution",
        attachment_type=allure.attachment_type.JSON,
    )

    plt_mod = None
    try:
        plt_mod = importlib.import_module("matplotlib.pyplot")
    except ModuleNotFoundError:
        plt_mod = None

    ticker_mod = None
    try:
        ticker_mod = importlib.import_module("matplotlib.ticker")
    except ModuleNotFoundError:
        ticker_mod = None

    if plt_mod is not None:
        fig, ax = plt_mod.subplots(figsize=(8.5, 5.2), dpi=120)
        _, rendered_edges, patches = ax.hist(scores, bins=edges, edgecolor="#2f2f2f", linewidth=1.0)
        for patch, left, right in zip(patches, rendered_edges[:-1], rendered_edges[1:]):
            center = (float(left) + float(right)) / 2.0
            patch.set_facecolor("#66bb6a" if center >= threshold else "#ef9a9a")

        ax.axvline(
            threshold,
            color="#1f2937",
            linestyle="--",
            linewidth=2,
            label=f"threshold = {threshold:.2f}",
        )
        ax.set_title(f"Histogram of {metric_bucket.replace('_', ' ')} scores")
        ax.set_xlabel("score")
        ax.set_ylabel("frequency")
        ax.set_xlim(0.0, 1.0)
        if ticker_mod is not None:
            ax.yaxis.set_major_locator(ticker_mod.MaxNLocator(integer=True))
            ax.yaxis.set_major_formatter(ticker_mod.StrMethodFormatter("{x:.0f}"))
        ax.grid(axis="y", alpha=0.25)
        ax.legend(loc="upper left")
        fig.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")
        plt_mod.close(fig)
        buffer.seek(0)
        png_bytes = buffer.getvalue()

        saved_path = _save_histogram_png(metric_bucket, png_bytes)
        allure.attach(
            str(saved_path),
            name=f"deepeval_{metric_bucket}_histogram_file_path",
            attachment_type=allure.attachment_type.TEXT,
        )

        allure.attach(
            png_bytes,
            name=f"deepeval_{metric_bucket}_score_distribution_histogram",
            attachment_type=allure.attachment_type.PNG,
        )

def _record_quality_score(metric_bucket: str, case_id: str, score: float, threshold: float) -> None:
    _QUALITY_SCORE_BUCKETS[metric_bucket].append(
        {
            "case_id": case_id,
            "score": float(score),
            "is_correct": bool(score >= threshold),
        }
    )

    if len(_QUALITY_SCORE_BUCKETS[metric_bucket]) == len(QUALITY_CASES):
        _attach_score_distribution(metric_bucket, threshold)

def _set_allure_quality_context(case: dict[str, object], metric_bucket: str) -> None:
    case_id = str(case.get("id", "unknown_case"))
    expected_intent = str(case.get("expected_intent", "unknown"))
    category = str(case.get("test_category", metric_bucket))

    allure.dynamic.parent_suite("MycoPortal Evaluation")
    allure.dynamic.suite(f"Dataset Mode: {DATASET_MODE}")
    allure.dynamic.sub_suite("Quality DeepEval")
    allure.dynamic.feature(f"Intent: {expected_intent}")
    allure.dynamic.story(metric_bucket)
    allure.dynamic.title(f"{case_id} [{metric_bucket}] ({DATASET_MODE})")

    allure.dynamic.tag(f"dataset_mode:{DATASET_MODE}")
    allure.dynamic.tag(f"intent:{expected_intent}")
    allure.dynamic.tag(f"category:{category}")
    if DATASET_ENDPOINT:
        allure.dynamic.tag(f"dataset_endpoint:{DATASET_ENDPOINT}")

    allure.attach(
        json.dumps(
            {
                "case_id": case_id,
                "metric_bucket": metric_bucket,
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

def _build_metric(name: str, evaluation_steps: list[str], threshold: float = 0.75):
    return GEval(
        name=name,
        evaluation_steps=evaluation_steps,
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

REASONING_STEPS = [
    "Check whether the reasoning explicitly mentions the user's request in concrete terms instead of using vague filler language.",
    "Check whether the reasoning explains why the selected tool fits the request and the expected intent.",
    "Check whether the reasoning references the query terms and the tool's actual capability, not an unrelated capability.",
    "Good reasoning is short, specific, and clearly links the query to the tool choice. Bad reasoning is generic, contradictory, or missing justification entirely.",
    "Score higher when the reasoning is grounded in the request and demonstrates correct semantic alignment.",
]

EXTRACTION_ACCURACY_STEPS = [
    "Check whether all required parameters for the intent are present and extracted (no missing critical fields).",
    "Check whether extracted parameter types are semantically correct (strings non-empty, integers positive where applicable, enums valid).",
    "Check whether extracted parameters are coherent with the query and the declared intent (e.g., search terms from query, identifiers numeric).",
    "Check whether parameter values satisfy domain constraints (e.g., limit > 0, offset >= 0, identifiers non-empty).",
    "Score higher when all parameters are correct, complete, semantically sound, and ready for API consumption.",
]

@pytest.mark.asyncio
@pytest.mark.quality
@pytest.mark.llm
@pytest.mark.parametrize("case", QUALITY_CASES, ids=[str(case["id"]) for case in QUALITY_CASES])
async def test_reasoning_and_tool_quality_with_deepeval(pipeline: dict[str, object], case: dict[str, object]) -> None:
    _set_allure_quality_context(case, "quality_reasoning")
    case_id = str(case.get("id", "unknown_case"))

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

    plan = await planner.plan(query)
    extraction = await extractor.extract(query, plan)
    allure.attach(json.dumps(plan.model_dump(), indent=2), name="planner_output", attachment_type=allure.attachment_type.JSON)

    allure.attach(
        json.dumps(extraction.model_dump(), indent=2),
        name="extraction_output",
        attachment_type=allure.attachment_type.JSON,
    )

    expected_reasoning = (
        f"The reasoning should justify the selected tool choice "
        f"and stay aligned with the {expected_intent} intent."
    )
    
    reasoning_metric = _build_metric(
        name="Reasoning Quality",
        evaluation_steps=REASONING_STEPS,
        threshold=REASONING_THRESHOLD,
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

    _record_quality_score("quality_reasoning", case_id, reasoning_score, reasoning_metric.threshold)

    assert reasoning_score >= reasoning_metric.threshold


@pytest.mark.asyncio
@pytest.mark.quality
@pytest.mark.llm
@pytest.mark.parametrize("case", QUALITY_CASES, ids=[str(case["id"]) for case in QUALITY_CASES])
async def test_extraction_parameter_accuracy_with_deepeval(pipeline: dict[str, object], case: dict[str, object]) -> None:
    _set_allure_quality_context(case, "quality_extraction")
    case_id = str(case.get("id", "unknown_case"))

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

    plan = await planner.plan(query)
    extraction = await extractor.extract(query, plan)

    extraction_dict = extraction.model_dump(exclude_none=True)
    actual_extraction_output = json.dumps(extraction_dict, indent=2)

    expected_extraction = (
        f"For intent '{expected_intent}', extraction should contain all required parameters "
        f"with correct types and values coherent with the query: '{query}'. "
        f"Strings must be non-empty, integers positive where applicable, and all domain constraints satisfied."
    )

    extraction_metric = _build_metric(
        name="Entity Extraction Accuracy",
        evaluation_steps=EXTRACTION_ACCURACY_STEPS,
        threshold=EXTRACTION_THRESHOLD,
    )
    extraction_score, extraction_reason = _measure_metric(
        extraction_metric,
        query,
        actual_extraction_output,
        expected_extraction,
    )

    allure.attach(
        json.dumps(
            {
                "query": query,
                "intent": expected_intent,
                "actual_extraction": extraction_dict,
                "score": extraction_score,
                "threshold": extraction_metric.threshold,
                "reason": extraction_reason,
            },
            indent=2,
        ),
        name="deepeval_extraction_metric",
        attachment_type=allure.attachment_type.JSON,
    )

    _record_quality_score("quality_extraction", case_id, extraction_score, extraction_metric.threshold)

    assert extraction_score >= extraction_metric.threshold
