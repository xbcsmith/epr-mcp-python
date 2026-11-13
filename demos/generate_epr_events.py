#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Generate sample CDEvents and event receivers and post them to EPR.

Creates 11 event receivers (one per CDEvent type) and 44 events (4 services times
11 types), then posts them, prints curl commands, or writes them to disk.

Usage:
    uv run python demos/generate_epr_events.py --dry-run
    uv run python demos/generate_epr_events.py --url http://localhost:8042
    uv run python demos/generate_epr_events.py --write-to-disk

Needs only httpx2. Exits 0 when everything was posted, 1 when any request failed.
"""

import argparse
import json
import logging
import os
import secrets
import shlex
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# httpx2 logs every request at INFO, which buries the demo output.
logging.getLogger("httpx2").setLevel(logging.WARNING)


def debug_except_hook(type, value, tb):
    """Print an uncaught exception and open a post-mortem debugger.

    Args:
        type: The exception class.
        value: The exception instance.
        tb: The traceback.

    Examples:
        ``sys.excepthook = debug_except_hook`` (installed when EPR_DEBUG is set).
    """
    print(f"epr python hates {type.__name__}")
    print(str(type))
    import pdb
    import traceback

    traceback.print_exception(type, value, tb)
    pdb.post_mortem(tb)


debug = os.environ.get("EPR_DEBUG", False)
if debug:
    sys.excepthook = debug_except_hook
    logger.setLevel(logging.DEBUG)


_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def generate_ulid() -> str:
    """Generate a ULID: a 48-bit millisecond timestamp plus 80 random bits, in Crockford base32.

    Returns:
        A 26 character ULID that sorts by creation time.

    Examples:
        >>> len(generate_ulid())
        26
    """
    value = ((time.time_ns() // 1_000_000) << 80) | secrets.randbits(80)
    return "".join(_CROCKFORD[(value >> shift) & 31] for shift in range(125, -1, -5))


# Function to get current timestamp in ISO format
def get_current_timestamp() -> str:
    """Get the current UTC time in ISO 8601 format.

    Returns:
        A timestamp such as ``2025-10-06T14:30:00.123456Z``.

    Examples:
        >>> get_current_timestamp().endswith("Z")
        True
    """
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def gen_sha(seed: str) -> str:
    """Generate a fake SHA-256 hash from a seed string.

    Args:
        seed: The text to hash.

    Returns:
        The 64 character hex digest.

    Examples:
        >>> len(gen_sha("foo"))
        64
    """
    import hashlib

    h = hashlib.sha256()
    h.update(seed.encode("utf-8"))
    return h.hexdigest()


def generate_event_receivers() -> List[Dict[str, Any]]:
    """Generate one event receiver for each supported CDEvents type.

    Returns:
        Eleven receiver dictionaries, each with name, version, description, type, and an empty schema.

    Examples:
        >>> len(generate_event_receivers())
        11
    """
    event_receivers: List[Dict[str, Any]] = []
    types = [
        "dev.cdevents.pipelinerun.started.0.2.0",
        "dev.cdevents.pipelinerun.queued.0.2.0",
        "dev.cdevents.artifact.packaged.0.2.0",
        "dev.cdevents.artifact.published.0.2.0",
        "dev.cdevents.build.started.0.2.0",
        "dev.cdevents.build.finished.0.2.0",
        "dev.cdevents.testcaserun.finished.0.2.0",
        "dev.cdevents.testsuiterun.finished.0.2.0",
        "dev.cdevents.environment.created.0.2.0",
        "dev.cdevents.service.deployed.0.2.0",
        "dev.cdevents.pipelinerun.finished.0.2.0",
    ]
    for event_type in types:
        name = "-".join(event_type.split(".")[:-3])
        version = ".".join(event_type.split(".")[-3:])
        description = " ".join(event_type.split(".")[:-3]).title()
        evr = dict(name=name, version=version, description=description, type=event_type, schema={})
        event_receivers.append(evr)
    return event_receivers


# Generate a series of CDEvents for different services and event types
def generate_events(evrs: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate one CDEvent of each supported type for each of four service names.

    Args:
        evrs: The posted receivers, keyed by CDEvents type, as returned by post_event_receivers; use an empty dictionary for a dry run.

    Returns:
        Forty-four event dictionaries that each point at their receiver's ID (a placeholder in a dry run).

    Examples:
        >>> len(generate_events({}))
        44
    """
    events: List[Dict[str, Any]] = []
    names = ["foo", "bar", "baz", "qux"]
    types = [
        "dev.cdevents.pipelinerun.started.0.2.0",
        "dev.cdevents.pipelinerun.queued.0.2.0",
        "dev.cdevents.artifact.packaged.0.2.0",
        "dev.cdevents.artifact.published.0.2.0",
        "dev.cdevents.build.started.0.2.0",
        "dev.cdevents.build.finished.0.2.0",
        "dev.cdevents.testcaserun.finished.0.2.0",
        "dev.cdevents.testsuiterun.finished.0.2.0",
        "dev.cdevents.environment.created.0.2.0",
        "dev.cdevents.service.deployed.0.2.0",
        "dev.cdevents.pipelinerun.finished.0.2.0",
    ]
    release = datetime.now(timezone.utc).strftime("%Y.%m.%d")
    for idx, name in enumerate(names, start=1):
        chain_id = generate_ulid()
        env_id = f"cluster/0{idx}"
        sha = gen_sha(f"{name}-{env_id}")
        artifact_id = f"pkg:oci/{name}@sha256:{sha}"
        subject_base_id = f"{name}-{generate_ulid()[:8]}"
        source = f"urn:generator:{name}"
        sbom_uri = f"https://sbom.repo/{name}/{generate_ulid()}.spdx"
        for event_type in types:
            ev_id = generate_ulid()
            ts = get_current_timestamp()
            subject_type = event_type.split(".")[2].strip()
            event_receiver_id = evrs.get(event_type, {}).get("data", "<replace_with_evr_id>")
            if subject_type == "testsuiterun":
                subject_type = "testSuiteRun"
            elif subject_type == "testcaserun":
                subject_type = "testCaseRun"

            context = {
                "version": "0.4.1",
                "id": ev_id,
                "chainId": chain_id,
                "source": source,
                "type": event_type,
                "timestamp": ts,
            }

            # Build subject content by event/subject type
            if "pipelinerun.started" in event_type or "pipelinerun.queued" in event_type:
                subject = {
                    "id": subject_base_id,
                    "type": "pipelineRun",
                    "content": {
                        "pipelineName": f"pipeline-{subject_base_id}",
                        "url": f"https://pipelines.example/run/{subject_base_id}",
                    },
                }
            elif "pipelinerun.finished" in event_type:
                subject = {
                    "id": subject_base_id,
                    "type": "pipelineRun",
                    "content": {
                        "pipelineName": f"pipeline-{subject_base_id}",
                        "url": f"https://pipelines.example/run/{subject_base_id}",
                        "outcome": "pass",
                    },
                }
            elif "artifact.packaged" in event_type:
                # artifact events (packaged / published)
                subject = {
                    "id": subject_base_id,
                    "type": "artifact",
                    "content": {
                        "change": {
                            "id": artifact_id,
                            "source": f"https://git.example/{name}.git",
                        },
                        "sbom": {
                            "uri": sbom_uri,
                        },
                    },
                }
            elif "artifact.published" in event_type:
                # artifact events (packaged / published)
                subject = {
                    "id": subject_base_id,
                    "type": "artifact",
                    "content": {
                        "sbom": {
                            "uri": sbom_uri,
                        },
                        "user": "robot",
                    },
                }
            elif "build" in event_type:
                subject = {
                    "id": subject_base_id,
                    "type": "build",
                    "source": f"https://git.example/{name}.git",
                    "content": {
                        "artifactId": artifact_id,
                    },
                }
                if "finished" in event_type:
                    subject["content"]["artifactId"] = artifact_id
            elif "testcaserun" in event_type:
                subject = {
                    "id": "myTestCaseRun123",
                    "source": f"https://git.example/{name}.git",
                    "type": "testCaseRun",
                    "content": {
                        "outcome": "pass",
                        "environment": {"id": env_id, "source": source},
                        "testCase": {
                            "id": generate_ulid(),
                            "version": "1.0",
                            "name": f"{name} integration test case",
                            "type": "integration",
                        },
                    },
                }
            elif "testsuiterun" in event_type:
                subject = {
                    "id": subject_base_id,
                    "type": "testSuiteRun",
                    "content": {
                        "environment": {"id": env_id, "source": source},
                        "outcome": "pass" if idx % 2 == 1 else "fail",
                        "testSuite": {
                            "id": generate_ulid(),
                            "version": "1.0",
                            "name": f"{name} integration tests",
                        },
                    },
                }
            elif "service" in event_type:
                subject = {
                    "id": subject_base_id,
                    "type": "service",
                    "content": {
                        "environment": {"id": env_id, "source": source},
                        "artifactId": artifact_id,
                    },
                }
            elif "environment" in event_type:
                subject = {
                    "id": env_id,
                    "type": "environment",
                    "content": {
                        "name": f"{name}-env-0{idx}",
                        "url": f"https://{name}-env-0{idx}.example.com",
                    },
                }
            else:
                subject = {"id": subject_base_id, "type": subject_type, "content": {}}

            event_template: Dict[str, Any] = {"context": context, "subject": subject}
            ev = dict(
                name=name,
                version="1.0.0",
                release=release,
                platform_id="x64-linux-oci-2",
                package="oci",
                description=f"{name} {event_type}",
                payload=event_template,
                success=True,
                event_receiver_id=event_receiver_id,
            )
            # debug output to stdout for visibility when running interactively
            logger.debug(json.dumps(ev, indent=2))
            events.append(ev)

    return events


def post(url, data, headers=None, timeout=10.0):
    """Post JSON to a URL and raise on any failure.

    Args:
        url: The full URL.
        data: The JSON body.
        headers: Optional request headers.
        timeout: Seconds to wait for a response.

    Returns:
        The successful response.

    Raises:
        httpx2.HTTPStatusError: If EPR answers with an error status.
        httpx2.HTTPError: If the request cannot be completed.

    Examples:
        ``post('http://localhost:8042/api/v1/events', event)``
    """
    try:
        with httpx2.Client(timeout=timeout) as client:
            response = client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response
    except httpx2.HTTPStatusError as e:
        print(f"HTTP error {e.response.status_code}: {e.response.text}")
        raise
    except Exception as e:
        print(f"Request failed: {e}")
        raise


def post_event_receiver(
    evr: Dict[str, Any],
    url: str = "http://localhost:8042",
    timeout: float = 10.0,
) -> httpx2.Response:
    """Post one event receiver to EPR.

    Args:
        evr: The receiver dictionary.
        url: The EPR base URL.
        timeout: Seconds to wait for a response.

    Returns:
        The successful response.

    Raises:
        httpx2.HTTPError: If the request fails or EPR answers with an error status.

    Examples:
        ``post_event_receiver(evr, url='http://localhost:8042')``
    """
    headers = {"Content-Type": "application/json"}
    endpoint = f"{url}/api/v1/receivers"
    resp = post(endpoint, data=evr, headers=headers, timeout=timeout)
    return resp


def post_event(
    event: Dict[str, Any],
    url: str = "http://localhost:8042",
    timeout: float = 10.0,
) -> httpx2.Response:
    """Post one event to EPR.

    Args:
        event: The event dictionary.
        url: The EPR base URL.
        timeout: Seconds to wait for a response.

    Returns:
        The successful response.

    Raises:
        httpx2.HTTPError: If the request fails or EPR answers with an error status.

    Examples:
        ``post_event(event, url='http://localhost:8042')``
    """
    headers = {"Content-Type": "application/json"}
    endpoint = f"{url}/api/v1/events"
    resp = post(endpoint, data=event, headers=headers, timeout=timeout)
    return resp


def post_event_receivers(
    evrs: List[Dict[str, Any]],
    url: str = "http://localhost:8042",
    timeout: float = 10.0,
) -> Dict[str, Dict[str, Any]]:
    """Post event receivers one after another.

    Args:
        evrs: The receiver dictionaries.
        url: The EPR base URL.
        timeout: Seconds to wait for each response.

    Returns:
        A dictionary keyed by receiver type; each value has ``status`` (None on failure) and ``data`` (the new ID, or the error).

    Examples:
        ``post_event_receivers(generate_event_receivers())``
    """
    results: Dict[str, Dict[str, Any]] = {}
    for evr in evrs:
        try:
            resp = post_event_receiver(evr, url=url, timeout=timeout)
            data = json.loads(resp.text)
            _id = data.get("data", "<no_id_returned>")
            results[evr["type"]] = dict(status=resp.status_code, data=_id)
        except Exception as e:
            results[evr["type"]] = dict(status=None, data=dict(error=str(e)))
    return results


def post_events(
    events: List[Dict[str, Any]],
    url: str = "http://localhost:8042",
    timeout: float = 10.0,
) -> List[Tuple[Optional[str], Optional[int], str]]:
    """Post events one after another; a failure is logged and recorded, not raised.

    Args:
        events: The event dictionaries.
        url: The EPR base URL.
        timeout: Seconds to wait for each response.

    Returns:
        A list of ``(event_id, status_code, response_text)`` tuples; the first two are None for a failed post.

    Examples:
        ``post_events(generate_events(receivers))``
    """
    results: List[Tuple[Optional[str], Optional[int], str]] = []
    for ev in events:
        try:
            resp = post_event(ev, url=url, timeout=timeout)
            ev_id = resp.json().get("data")
            results.append((ev_id, resp.status_code, resp.text))
        except Exception as e:
            nvrpp = ev.get("description", "<no_description>")
            logger.error(f"Failed to post event {nvrpp}: {e}")
            results.append((None, None, str(e)))
    return results


def make_curl_command(event: Dict[str, Any], url: str) -> str:
    """Build a curl command that posts the payload to a URL.

    Args:
        event: The JSON payload; it is shell-quoted.
        url: The URL to post to.

    Returns:
        The command line as a string.

    Examples:
        >>> make_curl_command({"a": 1}, "http://epr/x").startswith("curl -sS -X POST")
        True
    """
    # compact JSON to keep command shorter
    json_str = json.dumps(event, separators=(",", ":"), ensure_ascii=False)
    quoted_payload = shlex.quote(json_str)
    quoted_url = shlex.quote(url)
    return f"curl -sS -X POST -H 'Content-Type: application/json' -d {quoted_payload} {quoted_url}"


def main() -> int:
    """Generate receivers and events, then post them, print curl commands, or write files.

    Returns:
        0 if everything was posted (or a dry run or file write succeeded), 1 if any request failed.

    Examples:
        ``python demos/generate_epr_events.py --dry-run``
    """
    parser = argparse.ArgumentParser(
        description="Generate and post EPR event_receivers and events, print curl commands (dry-run), or write to disk."
    )
    parser.add_argument(
        "--url",
        "-u",
        default="http://localhost:8042",
        help="Webhook URL",
    )
    parser.add_argument("--timeout", "-t", type=float, default=10.0, help="Request timeout in seconds")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't send requests; print curl commands instead",
    )
    parser.add_argument(
        "--write-to-disk",
        action="store_true",
        help="Write events to disk as JSON files and skip posting",
    )
    args = parser.parse_args()

    url = args.url
    timeout = args.timeout

    event_receivers = generate_event_receivers()
    evr_results = {}
    if not args.dry_run:
        print(f"Posting {len(event_receivers)} event receivers to {url}/api/v1/receivers")
        evr_results = post_event_receivers(event_receivers, url=url, timeout=timeout)
    else:
        print("Dry run: curl commands for event receivers:")
        for evr in event_receivers:
            curl = make_curl_command(evr, f"{url}/api/v1/receivers")
            print(curl)

    if not args.dry_run:
        for evr_type, result in evr_results.items():
            status = result.get("status")
            status_str = str(status) if status is not None else "ERROR"
            print(f"{evr_type}: {status_str}")
    events = generate_events(evrs=evr_results)
    if args.write_to_disk:
        os.makedirs("epr_reports/event_receivers", exist_ok=True)
        for evr in event_receivers:
            evr_type = evr["type"]
            filename = f"epr_reports/event_receivers/{evr_type.replace('.', '_')}.json"
            with open(filename, "w") as f:
                json.dump(evr, f, indent=2)
            print(f"Wrote event receiver {evr_type} to {filename}")
        os.makedirs("epr_reports/events", exist_ok=True)
        for idx, event in enumerate(events, start=1):
            filename = f"epr_reports/events/event_{idx:03d}_{event['name']}_{event['version']}.json"
            with open(filename, "w") as f:
                json.dump(event, f, indent=2)
            print(f"Wrote event {event['payload']['context']['id']} to {filename}")
        print(f"Wrote {len(events)} events to disk in the 'epr_reports/events' directory")
        # Write curl commands
        with open("epr_reports/curl_commands_event_receivers.txt", "w") as f:
            for evr in event_receivers:
                curl = make_curl_command(evr, f"{url}/api/v1/receivers")
                f.write(curl + "\n")
        with open("epr_reports/curl_commands_events.txt", "w") as f:
            for event in events:
                curl = make_curl_command(event, f"{url}/api/v1/events")
                f.write(curl + "\n")
        print(
            "Wrote curl commands to epr_reports/curl_commands_event_receivers.txt and epr_reports/curl_commands_events.txt"
        )
    if args.dry_run:
        print("Dry run: curl commands for events:")
        for event in events:
            curl = make_curl_command(event, f"{url}/api/v1/events")
            print(curl)
    else:
        results = post_events(events, url=url, timeout=timeout)
        success = 0
        for ev_id, status, _ in results:
            status_str = str(status) if status is not None else "ERROR"
            print(f"{ev_id}: {status_str}")
            if status and 200 <= status < 300:
                success += 1
        print(f"Posted {success}/{len(results)} events successfully")
        failed_receivers = [t for t, r in evr_results.items() if r.get("status") is None]
        if failed_receivers or success != len(results):
            print(
                f"{len(failed_receivers)} event receivers and {len(results) - success} events failed",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
