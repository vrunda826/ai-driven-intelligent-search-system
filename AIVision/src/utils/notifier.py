"""Sends finalized track metadata to the ai-search and backend services (Members 2 & 3).

Both services are expected to expose a simple POST endpoint accepting a JSON
array of track metadata records matching shared/schemas/metadata_schema.json.
This module is deliberately fault-tolerant: if an endpoint isn't configured or
isn't reachable yet (e.g. during early development), it logs and moves on
rather than crashing the vision pipeline.
"""

import logging

import requests

logger = logging.getLogger(__name__)


def send_metadata(metadata: list, ai_search_endpoint: str = "", backend_endpoint: str = "",
                   timeout: float = 5.0) -> dict:
    """POST the metadata list to whichever endpoints are configured.

    Returns a dict of {endpoint_name: success_bool} for the caller to log/inspect.
    """
    results = {}

    for name, url in (("ai_search", ai_search_endpoint), ("backend", backend_endpoint)):
        if not url:
            logger.info("No endpoint configured for %s, skipping send.", name)
            results[name] = None
            continue
        try:
            response = requests.post(url, json=metadata, timeout=timeout)
            response.raise_for_status()
            logger.info("Sent %d track records to %s (%s)", len(metadata), name, url)
            results[name] = True
        except requests.exceptions.RequestException as e:
            logger.warning("Failed to send metadata to %s (%s): %s", name, url, e)
            results[name] = False

    return results
