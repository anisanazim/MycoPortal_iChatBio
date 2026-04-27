# MycoPortal Agent

Natural language fungal biodiversity agent built on iChatBio, backed by the MycoPortal Symbiota API.

## Documentation

| Resource | File |
|---|---|
| Technical documentation | [`MycoPortal_Agent_Documentation.pdf`](./MycoPortal_Agent_Documentation.pdf) |
| Data flow diagram | [`mycoportal_agent_data_flow_diagram.svg`](./mycoportal_agent_data_flow_diagram.svg) |

---

## What It Does

The agent accepts a natural-language query and runs a five-stage pipeline:

1. **Planner** — detects intent and selects tools
2. **Extractor** — pulls typed parameters from user text
3. **Resolver** — enriches identifiers when needed
4. **Router** — maps extraction output to API parameter models
5. **Executor** — calls MycoPortal endpoints and returns artifacts

## Supported Intents and Endpoints

| Intent | Endpoint |
|---|---|
| `occurrence_search` | `GET /api/v2/occurrence/search` |
| `occurrence_by_id` | `GET /api/v2/occurrence/{identifier}` |
| `taxonomy_search` | `GET /api/v2/taxonomy/search` |
| `taxon_by_id` | `GET /api/v2/taxonomy/{identifier}` |
| `collection_list` | `GET /api/v2/collection` |
| `media_lookup` | `GET /api/v2/media` |
| `morphology_list` | `GET /api/v2/morphology` |
| `exsiccata_list` | `GET /api/v2/exsiccata` |

## Project Layout

```
MycoPortal_iChatBio/
│
├── agent.py                               # Main MycoPortal agent definition
├── server.py                              # HTTP server entrypoint (port 9998)
├── requirements.txt                       # Python dependencies
├── env.yaml                               # Environment config (API keys) — gitignored
├── Dockerfile                             # Container build definition
├── README.md
├── .gitignore
├── __init__.py
│
├── MycoPortal_Agent_Documentation.pdf     # Full technical documentation
├── mycoportal_agent_data_flow_diagram.svg # End-to-end data flow diagram
│
├── common/                  # Shared utilities (config loader, helpers)
│   └── config.py
│
├── client/                  # MycoPortal API client
│   └── api.py
│
├── planning/                # Intent classification + tool planning
│   ├── planner.py
│   ├── models.py
│   └── capabilities/        # One .md per tool — loaded into planner prompt
│
├── extraction/              # Extractor schemas + field extraction logic
│   ├── extractor.py
│   └── models.py
│
├── resolution/              # Resolver for final agent responses
│   └── resolver.py
│
├── routing/                 # Router that maps extraction → API param models
│   └── router.py
│
├── execution/               # Tool execution layer (API calls, artifacts)
│   ├── executor.py
│   └── tools/               # One module per endpoint
│
├── models/                  # Shared Pydantic param models with validators
│   └── params.py
│
├── docs/                    # iChatBio reference documentation
│
└── tests/
    ├── conftest.py
    ├── data/                # JSON test datasets per endpoint
    ├── fixtures/            # FakeResponseContext mock
    └── integration/         # Functional + DeepEval quality tests
```

---

## Requirements

- Python 3.10+
- Dependencies from `requirements.txt`
- OpenAI-compatible endpoint credentials

## Configuration

Configuration is loaded from environment variables first, then `env.yaml` in the repo root.

**Required:**
- `OPENAI_API_KEY`

**Recommended:**
- `OPENAI_BASE_URL` (default: `https://api.openai.com/v1`)
- `MYCOPORTAL_API_BASE_URL` (default: `https://mycoportal.org/portal`)
- `MYCOPORTAL_HTTP_TIMEOUT` (default: `30`)

`env.yaml` format:

```yaml
OPENAI_API_KEY: sk-...
OPENAI_BASE_URL: https://api.openai.com/v1
MYCOPORTAL_API_BASE_URL: https://mycoportal.org/portal
MYCOPORTAL_HTTP_TIMEOUT: 30
```

> `env.yaml` is gitignored — never commit secrets to the repository.

---

## Install (Local)

```bash
git clone <repo-url>
cd MycoPortal_iChatBio

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Run (Local)

```bash
python server.py
# Server starts at http://0.0.0.0:9998
```

---

## Docker

### Build

```bash
docker build -t mycoportal-agent:1.1 .
```

### Run

`env.yaml` is gitignored and excluded from the Docker build context. Secrets must be injected at runtime.

**Option 1 — environment variables (recommended):**

```bash
docker run -p 29209:9998 \
  -e OPENAI_API_KEY=sk-... \
  -e OPENAI_BASE_URL=https://api.openai.com/v1 \
  mycoportal-agent:1.1
```

**Option 2 — `.env` file:**

`--env-file` requires `KEY=value` format, not YAML. Convert your `env.yaml` first:

```bash
sed 's/: /=/g' env.yaml > .env
```

Then run:

```bash
docker run -p 29209:9998 --env-file .env mycoportal-agent:1.1
```

> Add `.env` to `.gitignore` so it is never committed.

**Option 3 — volume mount:**

```bash
docker run -p 29209:9998 \
  -v $(pwd)/env.yaml:/app/env.yaml \
  mycoportal-agent:1.1
```

---

## Example Queries

- `Show fungal records recorded by smith in 2023`
- `Find Ganoderma occurrences in Florida`
- `Search taxonomy for names starting with Aspergillus`
- `Show me 50 live preserved-specimen collections starting from record 100`
- `Lookup media for taxon id 388665`
- `What morphological traits does MyCoPortal track?`
- `List all exsiccata`
- `Show occurrence details for identifier b1e1f38f-2873-4d98-bf34-404dd97074d4`

---

## Testing

### Run smoke tests (fastest — good for PRs)

```bash
pytest -m "smoke and functional" --alluredir=allure-results
```

### Run full evaluation

```bash
pytest -m "functional or quality" --alluredir=allure-results
```

### Run a single endpoint dataset

```bash
pytest --dataset-mode endpoint --endpoint taxonomy_search
```

### Run full regression across all endpoints

```bash
pytest --dataset-mode regression
```

### Generate Allure HTML report

```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

### Test markers

| Marker | Meaning |
|---|---|
| `functional` | End-to-end pipeline checks |
| `quality` | DeepEval semantic quality checks |
| `smoke` | Fast subset for PR validation |
| `llm` | Tests that call an LLM endpoint |
| `liveapi` | Tests that call live MycoPortal endpoints |
| `negative` | Expected-failure validation cases |

> Tests call live external services and can fail due to network issues or model variance.  
> If `OPENAI_API_KEY` is missing, LLM-dependent tests are skipped automatically.

---

## License / Data Source

This agent consumes read-only data from MycoPortal (Symbiota network).