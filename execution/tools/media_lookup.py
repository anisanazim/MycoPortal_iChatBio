from __future__ import annotations

from execution.tools.common import build_artifact_description, create_json_artifact
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
        request_summary = ", ".join(
            part
            for part in [
                f"tid {params.tid}" if params.tid is not None else None,
                "include synonyms" if params.includeSynonyms else None,
                "include children" if params.includeChildren else None,
            ]
            if part
        ) or None
        await create_json_artifact(
            process,
            description=build_artifact_description(
                "MycoPortal media lookup results",
                request_summary=request_summary,
                payload=payload,
            ),
            url=url,
            payload=payload,
            metadata={"search_params": params.model_dump(exclude_none=True)},
        )
        await context.reply("Media lookup completed. Results are available in the artifact.")
