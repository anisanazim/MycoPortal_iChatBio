from __future__ import annotations

from execution.tools.collection_list import run_collection_list
from execution.tools.exsiccata_list import run_exsiccata_list
from execution.tools.media_lookup import run_media_lookup
from execution.tools.morphology_list import run_morphology_list
from execution.tools.occurrence_by_id import run_occurrence_by_id
from execution.tools.occurrence_search import run_occurrence_search
from execution.tools.taxon_by_id import run_taxon_by_id
from execution.tools.taxonomy_search import run_taxonomy_search
from models.params import (
    CollectionListParams,
    ExsiccataListParams,
    MediaLookupParams,
    MorphologyListParams,
    OccurrenceByIdParams,
    OccurrenceSearchParams,
    TaxonByIdParams,
    TaxonomySearchParams,
)
from planning.models import PlannerOutput


class MycoPortalExecutor:
    """Execute routed MycoPortal tools in planner priority order."""

    def __init__(self, api):
        self.api = api

    async def execute(self, context, plan: PlannerOutput, routed: dict[str, object]) -> None:
        must_call = [t for t in plan.tools_planned if t.priority == "must_call"]
        optional = [t for t in plan.tools_planned if t.priority == "optional"]
        executed: list[str] = []

        async with context.begin_process("Executing MycoPortal tools") as process:
            await process.log(
                f"Tool plan: {[(t.tool_name, t.priority) for t in plan.tools_planned]}"
            )
            await process.log(f"Phase 1: {len(must_call)} must_call tool(s)")

            for tool_plan in must_call:
                if tool_plan.tool_name in executed:
                    await process.log(f"Skipping '{tool_plan.tool_name}' - already executed")
                    continue

                params = routed.get(tool_plan.tool_name)
                if params is None:
                    await process.log(f"No routed params for '{tool_plan.tool_name}' - skipping")
                    continue

                await process.log(f"Executing: {tool_plan.tool_name} - {tool_plan.reason}")

                try:
                    await self._call_tool(context, tool_plan.tool_name, params)
                    executed.append(tool_plan.tool_name)
                    await process.log(f"'{tool_plan.tool_name}' completed successfully")
                except Exception as e:
                    await process.log(f"'{tool_plan.tool_name}' FAILED: {e}")
                    await context.reply(f"A required operation failed: {e}")
                    return

            if optional:
                await process.log(f"Phase 2: {len(optional)} optional tool(s)")

            for tool_plan in optional:
                if tool_plan.tool_name in executed:
                    await process.log(f"Skipping '{tool_plan.tool_name}' - already executed")
                    continue

                params = routed.get(tool_plan.tool_name)
                if params is None:
                    await process.log(f"No routed params for '{tool_plan.tool_name}' - skipping")
                    continue

                await process.log(f"Executing optional: {tool_plan.tool_name} - {tool_plan.reason}")

                try:
                    await self._call_tool(context, tool_plan.tool_name, params)
                    executed.append(tool_plan.tool_name)
                    await process.log(f"'{tool_plan.tool_name}' completed")
                except Exception as e:
                    await process.log(f"Optional '{tool_plan.tool_name}' failed (continuing): {e}")

            await process.log(f"Execution complete: {len(executed)} tool(s) executed")

    async def _call_tool(self, context, tool_name: str, params: object) -> None:
        if tool_name == "search_occurrences":
            assert isinstance(params, OccurrenceSearchParams)
            await run_occurrence_search(context, self.api, params)
            return

        if tool_name == "get_occurrence_by_id":
            assert isinstance(params, OccurrenceByIdParams)
            await run_occurrence_by_id(context, self.api, params)
            return

        if tool_name == "search_taxonomy":
            assert isinstance(params, TaxonomySearchParams)
            await run_taxonomy_search(context, self.api, params)
            return

        if tool_name == "get_taxon_by_id":
            assert isinstance(params, TaxonByIdParams)
            await run_taxon_by_id(context, self.api, params)
            return

        if tool_name == "list_collections":
            assert isinstance(params, CollectionListParams)
            await run_collection_list(context, self.api, params)
            return

        if tool_name == "lookup_media":
            assert isinstance(params, MediaLookupParams)
            await run_media_lookup(context, self.api, params)
            return

        if tool_name == "list_morphology":
            assert isinstance(params, MorphologyListParams)
            await run_morphology_list(context, self.api, params)
            return

        if tool_name == "list_exsiccata":
            assert isinstance(params, ExsiccataListParams)
            await run_exsiccata_list(context, self.api, params)
            return

        raise ValueError(f"Unknown tool: {tool_name}")
