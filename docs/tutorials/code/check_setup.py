#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Preflight check for the workshop. Run it before the session and after any failure.

Usage:
    uv run python check_setup.py              # everything
    uv run python check_setup.py --skip-stdio # skip the slower editor-launch checks

Each line is PASS, FAIL, or SKIP. The first FAIL tells you what to fix.
"""

import argparse
import asyncio
import os
import shutil
import subprocess
import sys
from pathlib import Path

import httpx2
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

CODE_DIR = Path(__file__).resolve().parent
REPO_DIR = CODE_DIR.parents[2]
EPR_URL = os.environ.get("EPR_URL", "http://localhost:8042")
# Tool counts for the checkpoints that exist; checkpoint 01 only has one tool.
CHECKPOINTS = {"checkpoint_01_first_tool": 1, "checkpoint_03_tool_set": 9, "checkpoint_04_validation": 9}
FINAL_CHECKPOINT = "checkpoint_05_tests"
STDIO_TIMEOUT = 180  # the first uv run may download and install packages

failures = 0


def report(status: str, name: str, detail: str = "") -> None:
    """Print one result line and count failures.

    Args:
        status: PASS, FAIL, or SKIP.
        name: What was checked.
        detail: Optional extra text.

    Examples:
        ``report('PASS', 'Python 3.12 or newer', '3.12.11')``
    """
    global failures
    if status == "FAIL":
        failures += 1
    print(f"{status:<5}{name}" + (f": {detail}" if detail else ""))


def check_python() -> None:
    """Check that Python is 3.12 or newer.

    Examples:
        ``check_python()``
    """
    ok = sys.version_info >= (3, 12)
    report("PASS" if ok else "FAIL", "Python 3.12 or newer", sys.version.split()[0])


def check_uv() -> str | None:
    """Check that uv is on PATH.

    Returns:
        The path to uv, or None if it is missing.

    Examples:
        ``uv = check_uv()``
    """
    uv = shutil.which("uv")
    if not uv:
        report("FAIL", "uv on PATH", "install from https://docs.astral.sh/uv/")
        return None
    version = subprocess.run([uv, "--version"], capture_output=True, text=True).stdout.strip()
    report("PASS", "uv on PATH", f"{uv} ({version})")
    return uv


def check_epr() -> None:
    """Check that EPR answers its readiness endpoint.

    Examples:
        ``check_epr()``
    """
    try:
        response = httpx2.get(f"{EPR_URL}/healthz/readiness", timeout=5)
    except httpx2.HTTPError as error:
        report("FAIL", f"EPR reachable at {EPR_URL}", f"{error}; run 'docker compose up -d --build' in {CODE_DIR}")
        return
    ok = response.status_code == 200
    report("PASS" if ok else "FAIL", f"EPR ready at {EPR_URL}", f"HTTP {response.status_code}")


async def list_tools(transport: StdioTransport) -> list[str]:
    """Start a server over stdio and list its tools.

    Args:
        transport: The stdio transport that starts the server.

    Returns:
        The tool names.

    Examples:
        ``asyncio.run(list_tools(StdioTransport(command='python', args=['server.py'])))``
    """
    async with Client(transport, timeout=STDIO_TIMEOUT) as client:
        return [tool.name for tool in await client.list_tools()]


def check_in_process() -> None:
    """Start each checkpoint with the current Python and count its tools.

    Examples:
        ``check_in_process()``
    """
    servers = {name: (CODE_DIR / name / "server.py", count) for name, count in CHECKPOINTS.items()}
    servers["work (your server)"] = (CODE_DIR / "work" / "server.py", None)
    for name, (server, expected) in servers.items():
        label = f"{name} lists {expected} tool(s)" if expected else f"{name} lists at least one tool"
        if not server.exists():
            report("SKIP", label, "not created yet")
            continue
        try:
            tools = asyncio.run(
                list_tools(StdioTransport(command=sys.executable, args=[str(server)], log_file=Path(os.devnull)))
            )
        except Exception as error:
            report("FAIL", label, repr(error))
            continue
        ok = len(tools) == expected if expected else len(tools) > 0
        report("PASS" if ok else "FAIL", label, f"found {len(tools)}")


def check_editor_launch(uv: str) -> None:
    """Start servers with the exact commands the editor configs use.

    Args:
        uv: The path to uv.

    Examples:
        ``check_editor_launch('/usr/local/bin/uv')``
    """
    env = {**os.environ, "EPR_URL": EPR_URL}
    launches = {
        f"workshop server ({FINAL_CHECKPOINT}) via uv run": (
            CODE_DIR / FINAL_CHECKPOINT / "server.py",
            [uv, "run", "--directory", str(CODE_DIR), "python", f"{FINAL_CHECKPOINT}/server.py"],
            9,
        ),
        "shipped server (eprmcp) via uv run": (
            REPO_DIR / "pyproject.toml",
            [uv, "run", "--directory", str(REPO_DIR), "eprmcp", "start", "--transport", "stdio"],
            9,
        ),
    }
    for name, (required, command, expected) in launches.items():
        if not required.exists():
            report("SKIP", name, f"{required.name} not found")
            continue
        try:
            transport = StdioTransport(command=command[0], args=command[1:], env=env, log_file=Path(os.devnull))
            tools = asyncio.run(list_tools(transport))
        except Exception as error:
            report("FAIL", name, repr(error))
            continue
        report("PASS" if len(tools) == expected else "FAIL", name, f"found {len(tools)} tools")


def main() -> int:
    """Run all checks and print a summary.

    Returns:
        0 if every check passed or was skipped, 1 if any failed.

    Examples:
        ``uv run python check_setup.py --skip-stdio``
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skip-stdio", action="store_true", help="skip the uv run editor-launch checks")
    args = parser.parse_args()

    check_python()
    uv = check_uv()
    check_epr()
    check_in_process()
    if args.skip_stdio:
        report("SKIP", "editor-launch checks", "--skip-stdio")
    elif uv:
        check_editor_launch(uv)

    print()
    print("All checks passed." if not failures else f"{failures} check(s) failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
