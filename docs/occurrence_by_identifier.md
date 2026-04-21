# Occurrence By Identifier Endpoint

- Response schema: `get_occurrence_by_id`
- Tool: `get_occurrence_by_id`
- Endpoint: `GET /api/v2/occurrence/{identifier}`
- Symbiota service: Occurrence Detail Lookup

## Overview

This endpoint returns a single occurrence record by identifier (UUID). It is best for record detail retrieval when the exact occurrence ID is known.

## Identifier Input

Use a canonical UUID with hyphens.

## Occurrence Object Fields

Each response is a single occurrence object. Fields below are commonly useful for downstream responses.

| Field | Type | Description |
| --- | --- | --- |
| `occid` | `int` | Internal occurrence ID |
| `collid` | `int` | Internal collection ID |
| `dbpk` | `string` | Source database key/label |
| `basisOfRecord` | `string` | Occurrence type, for example preserved specimen |
| `occurrenceID` | `string` | Stable occurrence UUID |
| `catalogNumber` | `string` | Catalog number |
| `institutionCode` | `string` | Institution code |
| `collectionCode` | `string` | Collection code |
| `family` | `string` | Family name |
| `sciname` | `string` | Scientific name |
| `tidInterpreted` | `int` or `null` | Interpreted taxon ID |
| `genus` | `string` or `null` | Genus |
| `specificEpithet` | `string` or `null` | Species epithet |
| `scientificNameAuthorship` | `string` or `null` | Scientific name authorship |
| `identifiedBy` | `string` or `null` | Identifier(s) |
| `recordedBy` | `string` or `null` | Collector |
| `eventDate` | `string` or `null` | Event date string |
| `year` | `int` or `null` | Event year |
| `month` | `int` or `null` | Event month |
| `day` | `int` or `null` | Event day |
| `verbatimEventDate` | `string` or `null` | Original event date text |
| `associatedTaxa` | `string` or `null` | Related taxa/context |
| `country` | `string` or `null` | Country |
| `stateProvince` | `string` or `null` | State/province |
| `recordSecurity` | `int` | Security flag |
| `modified` | `string` or `null` | Source modified timestamp |
| `processingStatus` | `string` or `null` | Processing status |
| `recordID` | `string` | Record identifier |
| `dateEntered` | `string` | Created timestamp |
| `dateLastModified` | `string` or `null` | Last modified timestamp |

## What You Can Do With This Endpoint

- Retrieve one occurrence record when the identifier is known.
- Return record-level taxonomy, collector, and location metadata.
- Support detail panels and drill-down views from search results.