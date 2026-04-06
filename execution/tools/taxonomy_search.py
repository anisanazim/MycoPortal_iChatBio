from __future__ import annotations

from execution.tools.common import build_artifact_description, create_json_artifact
from models.params import TaxonomySearchParams


async def run_taxonomy_search(context, api, params: TaxonomySearchParams) -> None:
    async with context.begin_process("MycoPortal taxonomy search") as process:
        await process.log(
            "Search parameters",
            data=params.model_dump(exclude_none=True),
        )

        url = api.build_taxonomy_search_url(params)
        await process.log("API URL", data={"url": url})
        payload = await api.get_json(url)
        await create_json_artifact(
            process,
            description=build_artifact_description(
                "MycoPortal taxonomy search",
                request_summary=f"{params.taxon} ({params.type})",
                payload=payload,
            ),
            url=url,
            payload=payload,
            metadata={"taxon": params.taxon, "search_type": params.type},
        )
        await context.reply("Taxonomy search completed. Results are available in the artifact.")
