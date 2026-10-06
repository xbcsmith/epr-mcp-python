"""Checks that the workshop code and configs under docs/tutorials stay working.

Every checkpoint server must import and expose the right tools, the final
checkpoint's own tests must pass, and the editor configs must point at files
that exist.
"""

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest  # type: ignore
import yaml
from fastmcp import Client

TUTORIALS = Path(__file__).resolve().parents[2] / "docs" / "tutorials"
CODE = TUTORIALS / "code"
CHECKPOINTS = {
    "checkpoint_01_first_tool": 1,
    "checkpoint_03_tool_set": 9,
    "checkpoint_04_validation": 9,
    "checkpoint_05_tests": 9,
}
SHIPPED_TOOLS = {
    "fetch_event",
    "fetch_receiver",
    "fetch_group",
    "search_events",
    "search_receivers",
    "search_groups",
    "create_event",
    "create_receiver",
    "create_group",
}


def load_server(checkpoint: str):
    path = CODE / checkpoint / "server.py"
    spec = importlib.util.spec_from_file_location(f"workshop_{checkpoint}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("checkpoint", "expected"), CHECKPOINTS.items())
@pytest.mark.asyncio
async def test_checkpoint_server_lists_expected_tools(checkpoint, expected):
    module = load_server(checkpoint)
    async with Client(module.mcp) as client:
        tools = {tool.name for tool in await client.list_tools()}
    assert len(tools) == expected
    if expected == 9:
        assert tools == SHIPPED_TOOLS


def test_checkpoint_05_server_matches_checkpoint_04():
    """Module 05 only adds tests, so the server must not drift from module 04."""
    assert (CODE / "checkpoint_05_tests" / "server.py").read_text() == (
        CODE / "checkpoint_04_validation" / "server.py"
    ).read_text()


def test_checkpoint_05_own_tests_pass():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "checkpoint_05_tests", "-q", "-p", "no:cacheprovider"],
        cwd=CODE,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_vscode_config_references_existing_paths():
    config = json.loads((CODE / ".vscode" / "mcp.json").read_text())
    workshop = config["servers"]["epr-workshop"]["args"]
    assert (CODE / workshop[-1]).is_file()
    shipped = config["servers"]["epr-mcp"]["args"]
    assert (
        CODE / shipped[shipped.index("--directory") + 1].replace("${workspaceFolder}", ".") / "pyproject.toml"
    ).is_file()
    assert config["servers"]["epr-mcp"]["args"][-2:] == ["--transport", "stdio"]


def test_claude_desktop_config_matches_vscode_servers():
    desktop = json.loads((CODE / "claude_desktop_config.json").read_text())["mcpServers"]
    vscode = json.loads((CODE / ".vscode" / "mcp.json").read_text())["servers"]
    assert desktop.keys() == vscode.keys()
    for name in desktop:
        assert desktop[name]["args"][0] == "run"
        assert desktop[name]["args"][-1] == vscode[name]["args"][-1]


def test_workshop_compose_runs_only_epr_services():
    compose = yaml.safe_load((CODE / "docker-compose.yaml").read_text())
    assert set(compose["services"]) == {"postgres", "redpanda", "epr-server"}


def test_tutorial_files_are_named_per_agents_rules():
    for path in TUTORIALS.glob("*.md"):
        assert path.name == "README.md" or re.fullmatch(r"[0-9a-z_]+\.md", path.name), path.name


def test_tutorials_use_fastmcp_4_and_httpx2_only():
    stale = re.compile(
        r"mcp\.server\.fastmcp|^\s*import httpx\s*$|^\s*from httpx import|FastMCP 2|FastMCP 1|mcp\[cli\]", re.M
    )
    # Module 07 documents the migration, so it names the old APIs on purpose.
    migration_notes = TUTORIALS / "07_misc_and_troubleshooting.md"
    offenders = [
        str(p)
        for p in TUTORIALS.rglob("*")
        if p.suffix in {".md", ".py", ".toml"} and p != migration_notes and stale.search(p.read_text())
    ]
    assert offenders == []
