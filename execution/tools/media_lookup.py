from __future__ import annotations

from execution.tools.common import create_json_artifact
from models.params import MediaLookupParams


async def run_media_lookup(context, api, params: MediaLookupParams) -> None:
    async with context.begin_process("MycoPortal media lookup") as process:
        await process.log(
            "Search parameters",
            data=params.model_dump(exclude_none=True),
        )

        url = api.build_media_lookup_url(params)
        await process.log("API URL", data={"url": url})
        payload = await api.get_json(url)
        await create_json_artifact(
            process,
            description="MycoPortal media lookup results",
            url=url,
            payload=payload,
            metadata={"search_params": params.model_dump(exclude_none=True)},
        )
        await context.reply("Media lookup completed. Results are available in the artifact.")
