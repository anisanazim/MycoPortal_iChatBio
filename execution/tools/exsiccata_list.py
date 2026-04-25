from __future__ import annotations

from typing import TYPE_CHECKING

from execution.tools.common import build_artifact_description, create_json_artifact

if TYPE_CHECKING:
    from agent.context import Context
    from client.api import MycoPortalAPI
    from models.params import ExsiccataListParams


async def run_exsiccata_list(
    context: "Context",
    api: "MycoPortalAPI",
    params: "ExsiccataListParams",
) -> None:
    """Run the exsiccata list tool and display results."""
    async with context.begin_process("MycoPortal exsiccata listing") as process:
        await process.log(
            "Search parameters",
            data=params.model_dump(exclude_none=True),
        )

        url = api.build_exsiccata_list_url(params)
        await process.log("API URL", data={"url": url})
        payload = await api.get_json(url)
        request_summary = f"limit={params.limit}, offset={params.offset}"

        await create_json_artifact(
            process,
            description=build_artifact_description(
                "Exsiccata List",
                request_summary,
                payload,
            ),
            url=url,
            payload=payload,
            metadata={"schema": "exsiccata_list"},
        )
