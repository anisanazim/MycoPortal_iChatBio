from __future__ import annotations

from execution.tools.common import build_artifact_description, create_json_artifact
from models.params import CollectionListParams


async def run_collection_list(context, api, params: CollectionListParams) -> None:
    async with context.begin_process("MycoPortal collection listing") as process:
        await process.log(
            "Search parameters",
            data=params.model_dump(exclude_none=True),
        )

        url = api.build_collection_list_url(params)
        await process.log("API URL", data={"url": url})
        payload = await api.get_json(url)
        request_parts = [
            params.managementType,
            params.collectionType,
        ]
        request_summary = ", ".join(part for part in request_parts if part) or None
        await create_json_artifact(
            process,
            description=build_artifact_description(
                "MycoPortal collections",
                request_summary=request_summary,
                payload=payload,
            ),
            url=url,
            payload=payload,
            metadata={"search_params": params.model_dump(exclude_none=True)},
        )
        await context.reply("Collection listing completed. Results are available in the artifact.")
