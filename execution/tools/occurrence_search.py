from __future__ import annotations

from execution.tools.common import create_json_artifact
from models.params import OccurrenceSearchParams


async def run_occurrence_search(context, api, params: OccurrenceSearchParams) -> None:
    async with context.begin_process("MycoPortal occurrence search") as process:
        await process.log(
            "Search parameters",
            data=params.model_dump(exclude_none=True),
        )

        url = api.build_occurrence_search_url(params)
        await process.log("API URL", data={"url": url})
        payload = await api.get_json(url)

        total = payload.get("count", payload.get("total", payload.get("totalRecords", 0)))
        records = payload.get("results", payload.get("records", payload.get("occurrences", payload.get("data", []))))
        returned = len(records) if isinstance(records, list) else 0

        await process.log(f"Found {total:,} total records, returning {returned}")

        await create_json_artifact(
            process,
            description="MycoPortal occurrence search results",
            url=url,
            payload=payload,
            metadata={"total_matches": total, "search_params": params.model_dump(exclude_none=True)},
        )
        await context.reply("Occurrence search completed. Results are available in the artifact.")
