"""MycoPortal Agent HTTP server entrypoint."""

import sys
import os
import logging

# Path guard: ensure repo root is in sys.path when running from package folder
if __package__ is None:
    # Running as: cd mycoportal_agent; python server.py
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

from ichatbio.server import run_agent_server
from mycoportal_agent.agent import get_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Launch HTTP server on port 9998."""
    logger.info("Starting MycoPortal Agent Server at http://0.0.0.0:9998")
    agent = get_agent()
    card = agent.get_agent_card()
    logger.info(f"Agent: {card.name}")
    run_agent_server(agent, host="0.0.0.0", port=9998)


if __name__ == "__main__":
    main()
