#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Seed EPR with a receiver, a group, and a few events for the workshop.

Usage:
    uv run python seed_epr.py
    EPR_URL=http://other-host:8042 uv run python seed_epr.py

Prints the new IDs and saves them to seed_ids.json so later modules can use them.
Run it again to add another set; every run creates new records.
"""

import json
import os
import sys
from pathlib import Path

import httpx2

EPR_URL = os.environ.get("EPR_URL", "http://localhost:8042")
IDS_FILE = Path(__file__).with_name("seed_ids.json")

RECEIVER = {
    "name": "workshop.build",
    "type": "workshop.build",
    "version": "1.0.0",
    "description": "Receives build events for the workshop",
    "schema": {
        "type": "object",
        "properties": {"name": {"type": "string"}},
    },
}

EVENTS = [
    ("checkout-service", "1.2.3", True),
    ("checkout-service", "1.2.4", False),
    ("billing-service", "2.0.0", True),
]


def create(client: httpx2.Client, path: str, body: dict) -> str:
    """POST a record and return the new ID."""
    response = client.post(path, json=body)
    response.raise_for_status()
    return response.json()["data"]


def main() -> int:
    try:
        with httpx2.Client(base_url=EPR_URL, timeout=10) as client:
            receiver_id = create(client, "/api/v1/receivers", RECEIVER)
            group_id = create(
                client,
                "/api/v1/groups",
                {
                    "name": "workshop.builds",
                    "type": "workshop.builds",
                    "version": "1.0.0",
                    "description": "All workshop build receivers",
                    "event_receiver_ids": [receiver_id],
                },
            )
            event_ids = [
                create(
                    client,
                    "/api/v1/events",
                    {
                        "name": name,
                        "version": version,
                        "release": "2025.10.0",
                        "platform_id": "linux",
                        "package": "oci",
                        "description": f"Build of {name} {version}",
                        "payload": {"name": name},
                        "success": success,
                        "event_receiver_id": receiver_id,
                    },
                )
                for name, version, success in EVENTS
            ]
    except httpx2.ConnectError:
        print(f"Cannot reach EPR at {EPR_URL}. Run 'docker compose up -d --build' first.", file=sys.stderr)
        return 1
    except httpx2.HTTPStatusError as error:
        print(f"EPR returned {error.response.status_code}: {error.response.text}", file=sys.stderr)
        return 1

    ids = {"receiver_id": receiver_id, "group_id": group_id, "event_ids": event_ids}
    IDS_FILE.write_text(json.dumps(ids, indent=2) + "\n")
    print(json.dumps(ids, indent=2))
    print(f"Saved to {IDS_FILE.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
