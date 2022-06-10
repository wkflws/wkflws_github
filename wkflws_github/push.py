import json
import sys
from typing import Any

from wkflws.logging import getLogger


async def process_push(data: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Process push events from Github.

    Args:
        data: The push event from Github.
        context: Contextual information about the workflow being executed.
    """
    logger = getLogger("wkflws_github.push")
    logger.setLevel(10)
    logger.info("Processing Github push event...")
    return data


if __name__ == "__main__":
    import asyncio

    try:
        message = json.loads(sys.argv[1])
    except IndexError:
        raise ValueError("missing required `message` argument") from None

    try:
        context = json.loads(sys.argv[2])
    except IndexError:
        raise ValueError("missing `context` argument") from None

    output = asyncio.run(process_push(message, context))

    if output is None:
        sys.exit(1)

    print(json.dumps(output))
