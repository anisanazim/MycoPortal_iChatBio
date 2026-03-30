# MycoPortal Agent

Natural language fungal biodiversity agent built on iChatBio, backed by the MycoPortal Symbiota API.

## What It Does

The agent accepts a natural-language query and runs a five-stage pipeline:

1. Planner: detects intent and selects tools
2. Extractor: pulls typed parameters from user text
3. Resolver: enriches identifiers when needed
4. Router: maps extraction output to API parameter models
5. Executor: calls MycoPortal endpoints and returns artifacts

## Supported Intents and Endpoints

1. occurrence_search -> GET /api/v2/occurrence/search
2. occurrence_by_id -> GET /api/v2/occurrence/{identifier}
3. taxonomy_search -> GET /api/v2/taxonomy/search
4. taxon_by_id -> GET /api/v2/taxonomy/{identifier}
5. collection_list -> GET /api/v2/collection
6. media_lookup -> GET /api/v2/media

## Project Layout

- agent.py: Agent orchestration and pipeline wiring
- server.py: HTTP server entrypoint
- client/api.py: URL construction and HTTP GET wrapper
- planning/: intent planning and tool selection
- extraction/: schema-based parameter extraction
- resolution/: optional entity/identifier resolution
- routing/: extraction-to-params mapping
- execution/: tool handlers and execution orchestration
- models/: typed API parameter models

## Requirements

- Python 3.10+
- Dependencies from requirements.txt
- OpenAI-compatible endpoint credentials

## Configuration

Configuration is loaded from environment variables first, then env.yaml in repo root.

Required:
- OPENAI_API_KEY

Recommended:
- OPENAI_BASE_URL (default: https://api.openai.com/v1)
- MYCOPORTAL_API_BASE_URL (default: https://mycoportal.org/portal)


## Install

From the repository root:

pip install -r requirements.txt

## Run

python server.py

Server starts on:

http://0.0.0.0:9998

## Example Queries

- Show fungal records recorded by smith in 2023
- Find Ganoderma occurrences in Florida
- Search taxonomy for names starting with Aspergillus
- Show me 50 live preserved-specimen collections starting from record 100
- Lookup media for taxon id 388665


## License / Data Source

This agent consumes read-only data from MycoPortal (Symbiota network).