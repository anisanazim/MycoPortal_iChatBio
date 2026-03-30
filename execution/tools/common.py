from __future__ import annotations

import json
from datetime import datetime


async def create_json_artifact(process, description: str, url: str, payload: dict, metadata: dict | None = None) -> None:
    info = metadata or {}
    info.setdefault("data_source", "MycoPortal")
    info.setdefault("retrieval_date", datetime.now().strftime("%Y-%m-%d"))

    await process.create_artifact(
        mimetype="application/json",
        description=description,
        uris=[url],
        content=json.dumps(payload).encode("utf-8"),
        metadata=info,
    )
