# Taxon By ID Endpoint

- Response schema: `get_taxon_by_id`
- Tool: `get_taxon_by_id`
- Endpoint: `GET /api/v2/taxonomy/{identifier}`

## Overview

This endpoint returns a single taxonomy record for a specific taxon identifier.

## Response Structure

The response is a taxonomy object (not a paginated list).

### Core Taxon Fields

| Field | Type | Description |
| --- | --- | --- |
| `tid` | `int` | Taxon identifier |
| `scientificName` | `string` | Canonical scientific name |
| `kingdomName` | `string` or `null` | Kingdom name |
| `rankID` | `int` or `null` | Rank identifier |
| `rankName` | `string` or `null` | Rank name |
| `parentTid` | `int` or `null` | Parent taxon identifier |
| `status` | `string` or `null` | Taxon status, such as accepted/synonym |

### Name Construction Fields

| Field | Type | Description |
| --- | --- | --- |
| `unitInd1` | `string` or `null` | Rank indicator for unit name 1 |
| `unitName1` | `string` or `null` | Primary unit name |
| `unitInd2` | `string` or `null` | Rank indicator for unit name 2 |
| `unitName2` | `string` or `null` | Secondary unit name |
| `unitInd3` | `string` or `null` | Rank indicator for unit name 3 |
| `unitName3` | `string` or `null` | Tertiary unit name |
| `author` | `string` or `null` | Scientific name authorship |
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
| `modifiedTimestamp` | `string` or `null` | Last modified timestamp |
| `initialTimestamp` | `string` or `null` | Initial creation timestamp |

### Classification Lineage

| Field | Type | Description |
| --- | --- | --- |
| `classification` | `array` | Ordered lineage from higher ranks to parent taxon |

Each item in `classification[]` is a lineage node.

| Field | Type | Description |
| --- | --- | --- |
| `tid` | `int` | Lineage taxon identifier |
| `scientificName` | `string` | Lineage scientific name |
| `author` | `string` or `null` | Lineage authorship |
| `rankid` | `int` | Lineage rank identifier |

## What You Can Do With This Endpoint

- Retrieve full details for a known taxon identifier.
- Show taxonomy lineage/hierarchy for the selected taxon.
- Support drill-down views from taxonomy search results.
- Validate parent-child placement using `parentTid` and `classification`.