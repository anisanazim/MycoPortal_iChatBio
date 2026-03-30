from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

IntentType = Literal[
    "occurrence_search",
    "occurrence_by_id",
    "taxonomy_search",
    "taxon_by_id",
    "collection_list",
    "media_lookup",
    "out_of_scope",
    "unknown",
]

ToolName = Literal[
    "search_occurrences",
    "get_occurrence_by_id",
    "search_taxonomy",
    "get_taxon_by_id",
    "list_collections",
    "lookup_media",
]


class ToolPlan(BaseModel):
    tool_name: ToolName
    priority: Literal["must_call", "optional"] = "must_call"
    reason: str


class PlannerOutput(BaseModel):
    intent: IntentType
    tools_planned: list[ToolPlan] = Field(default_factory=list)
    reasoning: str
    clarification_needed: bool = False
    clarification_question: Optional[str] = None

    @model_validator(mode="after")
    def validate_tools(self) -> "PlannerOutput":
        if self.intent in ("out_of_scope", "unknown"):
            return self
        if not any(t.priority == "must_call" for t in self.tools_planned):
            raise ValueError(f"Intent '{self.intent}' requires one must_call tool")
        return self

    @model_validator(mode="after")
    def validate_clarification(self) -> "PlannerOutput":
        if self.clarification_needed and not self.clarification_question:
            raise ValueError("clarification_question is required when clarification_needed=True")
        return self
