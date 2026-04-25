# Tool: list_exsiccata

## Description

The `list_exsiccata` tool retrieves a paginated list of exsiccata (published, numbered sets of dried specimens) from the MycoPortal. This tool is ideal for users asking to browse, list, or find exsiccatum series.

## Triggering

This tool should be triggered for intents related to:

- Listing or browsing exsiccata.
- Searching for exsiccatum series.
- Inquiries about published specimen sets.

Example trigger phrases:

- "list all exsiccata"
- "show me the exsiccatum sets"
- "can you find the Fungi Bavarici series?"
- "browse published specimen collections"

## Parameters

This tool supports pagination using `limit` and `offset`.

- `limit`: The maximum number of records to return.
- `offset`: The starting index for pagination.

## Capabilities

- Fetches a list of all exsiccata.
- Supports pagination to browse through large result sets.

## Limitations

- This tool does not support searching or filtering by title, editor, or other fields. Filtering must be done client-side by the agent after retrieving the full list.
- It only lists the series, not the individual specimens within them.
