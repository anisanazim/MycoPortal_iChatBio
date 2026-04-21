# Media Lookup Endpoint

- Response schema: `lookup_media`
- Tool: `lookup_media`
- Endpoint: `GET /api/v2/media`

## Overview

This endpoint returns a paginated list of media records associated with taxa and/or occurrences.

## Response Structure

The response contains pagination metadata and a `results` array of media objects.

### Top-Level Fields

| Field | Type | Description |
| --- | --- | --- |
| `offset` | `int` | Starting index of returned records |
| `limit` | `int` | Maximum number of records returned |
| `endOfRecords` | `bool` | Whether additional records are available beyond this page |
| `count` | `int` | Total number of media records matching the query |
| `results` | `array` | List of media objects |

## Media Object Fields

Each item in `results[]` is one media record.

### Core Identity and Links

| Field | Type | Description |
| --- | --- | --- |
| `mediaID` | `int` | Media record identifier |
| `tid` | `int` or `null` | Taxon identifier linked to media |
| `occid` | `int` or `null` | Occurrence identifier linked to media |
| `recordID` | `string` or `null` | Media record UUID/identifier |
| `url` | `string` | Primary media URL |
| `thumbnailUrl` | `string` or `null` | Thumbnail URL |
| `originalUrl` | `string` or `null` | Original-size media URL |
| `archiveUrl` | `string` or `null` | Archive URL |
| `sourceUrl` | `string` or `null` | Source URL |
| `referenceUrl` | `string` or `null` | Reference URL |

### Media Description

| Field | Type | Description |
| --- | --- | --- |
| `imageType` | `string` or `null` | Image classification label |
| `mediaType` | `string` or `null` | Media type, for example image/audio/video |
| `format` | `string` or `null` | MIME type or format |
| `caption` | `string` or `null` | Caption text |
| `owner` | `string` or `null` | Owning collection or institution |
| `creator` | `string` or `null` | Creator name |
| `creatorUid` | `string` or `null` | Creator identifier |
| `locality` | `string` or `null` | Locality text tied to media |
| `anatomy` | `string` or `null` | Anatomy/body-part context |
| `notes` | `string` or `null` | Additional notes |

### Rights and Access

| Field | Type | Description |
| --- | --- | --- |
| `copyright` | `string` or `null` | Copyright statement |
| `rights` | `string` or `null` | Rights/license text or URL |
| `accessRights` | `string` or `null` | Access rights statement |

### Integrity and Dimensions

| Field | Type | Description |
| --- | --- | --- |
| `sourceIdentifier` | `string` or `null` | External source identifier |
| `hashFunction` | `string` or `null` | Hash algorithm |
| `hashValue` | `string` or `null` | Hash value |
| `mediaMD5` | `string` or `null` | MD5 checksum |
| `pixelXDimension` | `int` or `null` | Width in pixels |
| `pixelYDimension` | `int` or `null` | Height in pixels |

### Sorting and Lifecycle

| Field | Type | Description |
| --- | --- | --- |
| `sortSequence` | `int` or `null` | Sequence for display order |
| `sortOccurrence` | `int` or `null` | Secondary sort key |
| `initialTimestamp` | `string` or `null` | Initial creation timestamp |

## What You Can Do With This Endpoint

- Retrieve media linked to a taxon ID.
- Retrieve media linked to occurrence records.
- Build media galleries with thumbnails and original links.
- Filter and page through large media result sets.