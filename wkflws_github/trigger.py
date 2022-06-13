import json
from typing import Any, Optional

from wkflws.events import Event
from wkflws.http import http_method, Request
from wkflws.logging import getLogger
from wkflws.triggers.webhook import WebhookTrigger

from . import __identifier__, __version__

logger = getLogger("wkflws_github.trigger")
logger.setLevel(10)


async def process_webhook_request(request: Request) -> Optional[Event]:
    """Accept and process an HTTP request returning a event for the bus."""
    # 1. Create a unique identifier for the Event (this will become the workflow
    #    execution id)
    identifier = request.headers["x-github-delivery"]

    # 2. Convert the payload to a JSON serializable dictionary. For most cases it will
    #    be as simple as json.loads(request.body), but if you are given something else
    #    (such as XML) more care will need to be taken.
    data = json.loads(request.body)

    logger.info(f"Received Github webhook request {identifier}")

    # 3. Finally return the Event with as little modification to the data as possible.
    return Event(identifier, request.headers, data)


async def accept_event(event: Event) -> tuple[Optional[str], dict[str, Any]]:
    """Accept and process data from the event bus."""
    data = event.data

    # There is no real way of knowing what type of github event was sent/accepted from
    # the payload alone, so the header has to be included.
    data["x-github-event"] = event.metadata["x-github-event"]

    event_type = event.metadata["x-github-event"]

    logger.info(f"Processing Github webhook as '{event_type}' event")
    match event_type:
        case "ping":
            # Github sends a no-op ping request when subscribing to webhooks.
            return None, {}
        case "pull_request":
            return "wkflws_github.pull_request", data
        case "push":
            return "wkflws_github.push", data
        case _:
            logger.error(
                f"Received unsupported github event type '{event_type}' "
                f"(id:{event.identifier})"
            )
            return None, {}


my_webhook_trigger = WebhookTrigger(
    client_identifier=__identifier__,
    client_version=__version__,
    process_func=accept_event,
    routes=(
        (
            (http_method.POST,),
            "/webhook/",
            process_webhook_request,
        ),
    ),
)
