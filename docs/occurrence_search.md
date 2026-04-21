# Occurrence Search Endpoint

- Response schema: `search_occurrences`
- Tool: `search_occurrences`
- Endpoint: `GET /api/v2/occurrence/search`

## Overview

This endpoint returns a paginated list of occurrence records (specimen-level records) matching search filters.

## Response Structure

The response contains pagination metadata and a `results` array of occurrence objects.

### Top-Level Fields

| Field | Type | Description |
| --- | --- | --- |
| `offset` | `int` | Starting index of returned records |
| `limit` | `int` | Maximum number of records returned |
| `endOfRecords` | `bool` | Whether additional records are available beyond this page |
| `count` | `int` | Total number of records matching the query |
| `results` | `array` | List of occurrence objects |

## Occurrence Object Fields

Each item in `results[]` is one occurrence record.

### Core Identity

| Field | Type | Description |
| --- | --- | --- |
| `occid` | `int` | Internal occurrence ID |
| `occurrenceID` | `string` | Stable occurrence UUID |
| `recordID` | `string` | Record identifier (often same as `occurrenceID`) |
| `basisOfRecord` | `string` | Record type, for example `PreservedSpecimen` |
| `collid` | `int` | Internal collection ID |
| `dbpk` | `string` | Source database primary key label |

### Catalog and Institution

| Field | Type | Description |
| --- | --- | --- |
| `catalogNumber` | `string` | Collection catalog number |
| `institutionCode` | `string` | Institution code |
| `collectionCode` | `string` | Collection code |

### Taxonomy

| Field | Type | Description |
| --- | --- | --- |
| `family` | `string` | Family name |
| `sciname` | `string` | Scientific name string |
| `tidInterpreted` | `int` or `null` | Interpreted taxon ID |
| `genus` | `string` or `null` | Genus name |
| `specificEpithet` | `string` or `null` | Species epithet |
| `taxonRank` | `string` or `null` | Taxonomic rank |

### Collector and Event

| Field | Type | Description |
| --- | --- | --- |
| `recordedBy` | `string` or `null` | Primary collector name |
| `associatedCollectors` | `string` or `null` | Additional collectors |
| `eventDate` | `string` or `null` | Event date string |
| `year` | `int` or `null` | Event year |
| `month` | `int` or `null` | Event month |
| `day` | `int` or `null` | Event day |
| `verbatimEventDate` | `string` or `null` | Original date text |

### Location and Coordinates

| Field | Type | Description |
| --- | --- | --- |
| `country` | `string` or `null` | Country value |
| `stateProvince` | `string` or `null` | State or province |
| `county` | `string` or `null` | County |
| `locality` | `string` or `null` | Locality description |
| `decimalLatitude` | `number` or `null` | Latitude |
| `decimalLongitude` | `number` or `null` | Longitude |
| `geodeticDatum` | `string` or `null` | Coordinate reference datum |
| `coordinateUncertaintyInMeters` | `number` or `null` | Coordinate uncertainty |

### Record Lifecycle

| Field | Type | Description |
| --- | --- | --- |
| `dateEntered` | `string` | Record creation timestamp |
| `modified` | `string` or `null` | Last modified timestamp (source field) |
| `dateLastModified` | `string` or `null` | Last modified timestamp |
| `processingStatus` | `string` or `null` | Processing state |
| `recordSecurity` | `int` | Security flag |

## What You Can Do With This Endpoint

- Search and paginate occurrence records.
- Retrieve specimen-level metadata for matched records.
- Filter by taxonomy, collector, catalog number, date, and geography.
- Build downstream views for taxonomy distribution and collection summaries.

## Data Quality Notes (From Sample)

- Some records may use placeholder dates like `0000-00-00`, with `year/month/day` equal to `0`.
- Many fields can be `null` depending on source data quality.
- Country or locality values may be sparse or generic (for example `Unknown`).
- `occurrenceID` and `recordID` may be the same value in many records.