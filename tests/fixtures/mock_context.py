from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FakeArtifact:
    mimetype: str
    description: str
    uris: list[str]
    content: bytes
    metadata: dict[str, Any] = field(default_factory=dict)


class FakeProcess:
    def __init__(self, context: "FakeResponseContext", name: str):
        self.context = context
        self.name = name
        self.logs: list[dict[str, Any]] = []

    async def __aenter__(self) -> "FakeProcess":
        self.context.process_names.append(self.name)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def log(self, message: str, data: dict[str, Any] | None = None) -> None:
        entry = {"message": message}
        if data is not None:
            entry["data"] = data
        self.logs.append(entry)
        self.context.logs.append(entry)

    async def create_artifact(
        self,
        mimetype: str,
        description: str,
        uris: list[str],
        content: bytes,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.context.artifacts.append(
            FakeArtifact(
                mimetype=mimetype,
                description=description,
                uris=uris,
                content=content,
                metadata=metadata or {},
            )
        )


class FakeResponseContext:
    def __init__(self):
        self.replies: list[str] = []
        self.artifacts: list[FakeArtifact] = []
        self.logs: list[dict[str, Any]] = []
        self.process_names: list[str] = []

    def begin_process(self, name: str) -> FakeProcess:
        return FakeProcess(self, name)

    async def reply(self, message: str) -> None:
        self.replies.append(message)
