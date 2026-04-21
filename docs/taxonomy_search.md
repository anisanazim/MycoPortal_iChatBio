# Taxonomy Search Endpoint

- Response schema: `search_taxonomy`
- Tool: `search_taxonomy`
- Endpoint: `GET /api/v2/taxonomy/search`

## Overview

This endpoint returns a paginated list of taxonomy records that match a name query.

## Response Structure

The response contains pagination metadata and a `results` array of taxonomy objects.


### Core Taxon Fields

| Field | Type | Description |
| --- | --- | --- |
| `tid` | `int` | Taxon identifier |
| `scientificName` | `string` | Canonical scientific name display value |
| `kingdomName` | `string` or `null` | Kingdom name |
| `rankID` | `int` or `null` | Rank identifier |
| `rankName` | `string` or `null` | Rank label |

### Name Construction Fields

| Field | Type | Description |
| --- | --- | --- |
| `unitInd1` | `string` or `null` | Rank indicator for unit name 1 |
| `unitName1` | `string` or `null` | Primary unit name |
| `unitInd2` | `string` or `null` | Rank indicator for unit name 2 |
| `unitName2` | `string` or `null` | Secondary unit name |
| `unitInd3` | `string` or `null` | Rank indicator for unit name 3 |
| `unitName3` | `string` or `null` | Tertiary unit name |
| `author` | `string` or `null` | Name authorship |
| `cultivarEpithet` | `string` or `null` | Cultivar epithet |
| `tradeName` | `string` or `null` | Trade name |

### Status and Metadata Fields

| Field | Type | Description |
| --- | --- | --- |
| `reviewStatus` | `string` or `null` | Review status flag |
| `displayStatus` | `string` or `null` | Display status flag |
| `isLegitimate` | `int` or `bool` or `null` | Legitimacy indicator |
| `source` | `string` or `null` | Source authority or dataset |
| `notes` | `string` or `null` | Additional notes |
| `securityStatus` | `int` | Security flag |
| `modifiedTimestamp` | `string` | Last modified timestamp |
| `initialTimestamp` | `string` | Initial creation timestamp |

## What You Can Do With This Endpoint

- Search taxon names by exact, prefix, whole-word, or wildcard matching.
- Retrieve taxonomy metadata for user-selected names.
- Populate taxon pickers and autocomplete flows.
- Provide ranked taxonomy search results for follow-up actions.