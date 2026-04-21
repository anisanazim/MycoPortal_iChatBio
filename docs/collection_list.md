# Collection List Endpoint

- Response schema: `list_collections`
- Tool: `list_collections`
- Endpoint: `GET /api/v2/collection`

## Overview

This endpoint returns a paginated list of collection records and their institutional metadata.

## Response Structure

The response contains pagination metadata and a `results` array of collection objects.

### Top-Level Fields

| Field | Type | Description |
| --- | --- | --- |
| `offset` | `int` | Starting index of returned records |
| `limit` | `int` | Maximum number of records returned |
| `endOfRecords` | `bool` | Whether additional records are available beyond this page |
| `count` | `int` | Total number of collection records matching the query |
| `results` | `array` | List of collection objects |

## Collection Object Fields

Each item in `results[]` is one collection record.

### Core Collection Identity

| Field | Type | Description |
| --- | --- | --- |
| `collID` | `int` | Internal collection identifier |
| `collectionID` | `string` | Collection GUID/UUID |
| `collectionGuid` | `string` | Collection GUID/UUID alias |
| `collectionName` | `string` | Collection display name |
| `institutionCode` | `string` | Institution code |
| `collectionCode` | `string` | Collection code |
| `iid` | `int` or `null` | Internal institution identifier |

### Dataset and Description

| Field | Type | Description |
| --- | --- | --- |
| `datasetID` | `string` or `null` | Dataset identifier |
| `datasetName` | `string` or `null` | Dataset name |
| `fullDescription` | `string` or `null` | Collection description |
| `homepage` | `string` or `null` | Collection homepage URL |
| `individualUrl` | `string` or `null` | Collection detail URL |
| `resourceJson` | `string` or `null` | JSON-encoded list of external resources |

### Contact and Access

| Field | Type | Description |
| --- | --- | --- |
| `Contact` | `string` or `null` | Primary contact text |
| `email` | `string` or `null` | Primary contact email |
| `contactJson` | `string` or `null` | JSON-encoded contact list |
| `accessRights` | `string` or `null` | Access rights statement |
| `rightsHolder` | `string` or `null` | Rights holder |
| `rights` | `string` or `null` | Rights/license URL or text |
| `usageTerm` | `string` or `null` | Usage terms |

### Location and Media

| Field | Type | Description |
| --- | --- | --- |
| `latitudeDecimal` | `number` or `null` | Latitude for collection/institution location |
| `longitudeDecimal` | `number` or `null` | Longitude for collection/institution location |
| `icon` | `string` or `null` | Collection icon path |
| `dwcaUrl` | `string` or `null` | Darwin Core Archive download URL |

### Classification and Lifecycle

| Field | Type | Description |
| --- | --- | --- |
| `collType` | `string` or `null` | Collection type |
| `managementType` | `string` or `null` | Data management mode |
| `publicEdits` | `int` or `null` | Public edit flag |
| `recordID` | `string` or `null` | Record identifier |
| `bibliographicCitation` | `string` or `null` | Citation text |
| `sortSeq` | `int` or `null` | Sort sequence |
| `initialTimestamp` | `string` or `null` | Initial creation timestamp |

## What You Can Do With This Endpoint

- List all available collections in the portal.
- Filter and page through live/snapshot collections.
- Display collection metadata, licensing, and contact information.
- Surface data download links such as Darwin Core Archives.
