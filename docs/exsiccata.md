# Exsiccata Endpoint

- Endpoint: `GET /api/v2/exsiccata`
- Symbiota service: Exsiccatum (Dried Specimen Sets)

## Overview

This endpoint returns a paginated list of exsiccata, which are published, numbered sets of dried specimens.

## Query Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `limit` | `int` | The maximum number of records to return. |
| `offset` | `int` | The starting index for the records to return, used for pagination. |

## Response Structure

The response contains pagination metadata and a `results` array of exsiccatum objects.

### Top-Level Fields

| Field | Type | Description |
| --- | --- | --- |
| `offset` | `int` | Starting index of the returned slice. |
| `limit` | `int` | Maximum number of records returned. |
| `endOfRecords` | `boolean` | Indicates if there are more records to fetch. |
| `count` | `int` | Total number of exsiccata available. |
| `results` | `array` | List of exsiccatum objects. |

### Exsiccatum Fields

Each item in `results[]` is one exsiccatum.

| Field | Type | Description |
| --- | --- | --- |
| `ometid` | `int` | Unique identifier for the exsiccatum. |
| `title` | `string` | The title of the exsiccatum series. |
| `abbreviation` | `string` | The standard abbreviation for the series. |
| `editor` | `string` | The editor(s) of the series. |
| `exsrange` | `string` | The range of numbers in the series. |
| `startdate` | `string` | The publication start date of the series. |
| `enddate` | `string` | The publication end date of the series. |
| `source` | `string` | The source of the information about the series. |
| `sourceIdentifier` | `string` | A URL or other identifier for the source. |
| `notes` | `string` | Additional notes about the series. |
| `recordID` | `string` | An associated record ID. |
| `initialtimestamp` | `string` | Timestamp when the record was first created. |
