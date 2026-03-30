from pathlib import Path

CAPABILITIES_DIR = Path(__file__).parent / "capabilities"


class ToolCapabilityRegistry:
    """Loads MycoPortal tool capability docs for planner prompt grounding."""

    def __init__(self):
        self._capabilities: dict[str, str] = {}
        self._load_all()

    def _load_all(self) -> None:
        for path in sorted(CAPABILITIES_DIR.glob("*.md")):
            self._capabilities[path.stem] = path.read_text(encoding="utf-8")

    def get_all_for_planner(self) -> str:
        return "\n\n---\n\n".join(self._capabilities.values())


registry = ToolCapabilityRegistry()
