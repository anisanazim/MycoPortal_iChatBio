# Morphological Characters Endpoint

- Response schema: `get_morphological_characters`
- Tool: `get_morphological_characters`
- Endpoint: `GET /api/v2/morphology`
- Symbiota service: Morphological Character Definitions

## Overview

This endpoint returns a paginated list of morphological character definitions. These are trait definitions, not specimen-level trait values. 

## Response Structure

The response contains pagination metadata and a `results` array of character definitions.

### Top-Level Fields

| Field | Type | Description |
| --- | --- | --- |
| `offset` | `int` | Starting index of the returned slice |
| `limit` | `int` | Maximum number of records returned |
| `count` | `int` | Total number of morphological characters available |
| `results` | `array` | List of morphological character objects |

### Morphological Character Fields

Each item in `results[]` is one morphological character definition.

| Field | Type | Description |
| --- | --- | --- |
| `cid` | `int` | Unique character ID |
| `charName` | `string` | Human-readable name of the morphological character |
| `charType` | `string` | Character type code (for example `UM`, `TX`) |
| `defaultLang` | `string` | Language of the character label (usually `English`) |
| `hid` | `int` | Higher-level grouping ID used by UI ordering/grouping |
| `sortSequence` | `int` | Ordering index inside its group |
| `enteredBy` | `string` | Creator of the character definition |
| `initialTimestamp` | `string` | Timestamp when the character was first created |

## What You Can Do With This Endpoint

- List morphology characters.
- Search or filter by character name in agent-side logic.
- Explain what kinds of traits are represented in the portal.
- Build UI lists such as filters and dropdowns.

## What This Endpoint Does Not Provide

- Specimen-level trait values.
- Trait states/options for each character.
- Taxon-specific applicability of a character.
- Controlled vocabularies linked to each character.