import sys
import os
import logging
from ichatbio.server import run_agent_server
from agent import get_agent
from typing import Optional

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