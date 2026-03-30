from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ResolutionResult(BaseModel):
    clarification_needed: bool = Field(default=False)
    clarification_question: Optional[str] = Field(default=None)
