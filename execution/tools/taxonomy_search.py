from __future__ import annotations

from mycoportal_agent.execution.tools.common import create_json_artifact
from mycoportal_agent.models.params import TaxonomySearchParams


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
            description=f"MycoPortal taxonomy search: {params.taxon}",
            url=url,
            payload=payload,
            metadata={"taxon": params.taxon, "search_type": params.type},
        )
        await context.reply("Taxonomy search completed. Results are available in the artifact.")
