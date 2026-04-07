__all__ = ["MycoPortalAgent"]


def __getattr__(name: str):
	# Defer importing runtime-heavy modules until explicitly requested.
	if name == "MycoPortalAgent":
		from .agent import MycoPortalAgent

		return MycoPortalAgent
	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
