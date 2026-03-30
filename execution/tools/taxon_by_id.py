from __future__ import annotations

from mycoportal_agent.execution.tools.common import create_json_artifact
from mycoportal_agent.models.params import TaxonByIdParams


async def run_taxon_by_id(context, api, params: TaxonByIdParams) -> None:
    async with context.begin_process("MycoPortal taxon lookup") as process:
        await process.log(
            "Lookup parameters",
            data=params.model_dump(exclude_none=True),
        )

        url = api.build_taxon_by_id_url(params)
        await process.log("API URL", data={"url": url})
        payload = await api.get_json(url)
        await create_json_artifact(
            process,
            description=f"MycoPortal taxon record: {params.identifier}",
            url=url,
            payload=payload,
            metadata={"identifier": params.identifier},
        )
        await context.reply(f"Taxon lookup completed for tid {params.identifier}.")
