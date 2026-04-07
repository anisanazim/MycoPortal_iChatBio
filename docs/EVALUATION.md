# Evaluation Guide

This project supports automated agent evaluation with pytest, DeepEval, and Allure.

## Prerequisites

- Python 3.10+
- OPENAI_API_KEY configured via environment variable or env.yaml
- Optional: OPENAI_BASE_URL if you use a custom endpoint
- Java (for local Allure HTML report generation)

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run smoke evaluation

```bash
pytest -m "smoke and functional" --alluredir=allure-results
```

## Run full evaluation

```bash
pytest -m "functional or quality" --alluredir=allure-results
```

## Generate local Allure report

```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

## Test markers

- functional: end-to-end functional pipeline checks
- quality: DeepEval semantic quality checks
- smoke: fast subset for PR checks
- llm: tests that call an LLM endpoint
- liveapi: tests that call live MycoPortal endpoints

## Notes

- These tests call live external services and can fail due to network issues or model variance.
- Keep smoke tests lightweight for pull requests and run full quality suites on a schedule.
- If OPENAI_API_KEY is missing, LLM-dependent tests are skipped.
