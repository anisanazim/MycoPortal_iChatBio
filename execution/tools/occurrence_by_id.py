from __future__ import annotations

from execution.tools.common import build_artifact_description, create_json_artifact
from models.params import OccurrenceByIdParams


async def run_occurrence_by_id(context, api, params: OccurrenceByIdParams) -> None:
    async with context.begin_process("MycoPortal occurrence lookup") as process:
        await process.log(
            "Lookup parameters",
            data=params.model_dump(exclude_none=True),
        )

        url = api.build_occurrence_by_id_url(params)
        await process.log("API URL", data={"url": url})
        payload = await api.get_json(url)
        await create_json_artifact(
            process,
            description=build_artifact_description(
                "MycoPortal occurrence record",
                request_summary=params.identifier,
                payload=payload,
            ),
            url=url,
            payload=payload,
            metadata={"identifier": params.identifier},
        )
        await context.reply(f"Occurrence record lookup completed for identifier {params.identifier}.")
