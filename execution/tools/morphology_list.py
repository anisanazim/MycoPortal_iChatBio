from __future__ import annotations

from execution.tools.common import build_artifact_description, create_json_artifact
from models.params import MorphologyListParams


async def run_morphology_list(context, api, params: MorphologyListParams) -> None:
    async with context.begin_process("MycoPortal morphology listing") as process:
        await process.log(
            "Search parameters",
            data=params.model_dump(exclude_none=True),
        )

        url = api.build_morphology_list_url(params)
        await process.log("API URL", data={"url": url})
        payload = await api.get_json(url)
        request_summary = "with states" if params.includeStates == 1 else "without states"
        await create_json_artifact(
            process,
            description=build_artifact_description(
                "MycoPortal morphology characters",
                request_summary=request_summary,
                payload=payload,
            ),
            url=url,
            payload=payload,
            metadata={"search_params": params.model_dump(exclude_none=True)},
        )
        await context.reply("Morphology listing completed. Results are available in the artifact.")
