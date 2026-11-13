# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Smoke tests for the demo scripts. None of them need EPR or the network."""

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest  # type: ignore

DEMOS = Path(__file__).resolve().parents[2] / "demos"


def load(name: str):
    """Import a demo script from the demos directory as a module."""
    spec = importlib.util.spec_from_file_location(f"demo_{name}", DEMOS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generator():
    """Provide the generate_epr_events module."""
    return load("generate_epr_events")


class TestGenerateEprEvents:
    """Tests for demos/generate_epr_events.py."""

    def test_ulids_are_valid_and_sortable(self, generator):
        """Test ulids are valid and sortable."""
        ids = [generator.generate_ulid() for _ in range(50)]
        assert all(re.fullmatch(r"[0-9A-HJKMNP-TV-Z]{26}", value) for value in ids)
        assert len(set(ids)) == 50

    def test_ulid_timestamp_prefix_orders_by_time(self, generator, monkeypatch):
        """Test ulid timestamp prefix orders by time."""
        monkeypatch.setattr(generator.time, "time_ns", lambda: 1_000_000_000_000)
        earlier = generator.generate_ulid()
        monkeypatch.setattr(generator.time, "time_ns", lambda: 2_000_000_000_000)
        later = generator.generate_ulid()
        assert earlier[:10] < later[:10]

    def test_receivers_cover_eleven_cdevent_types_with_a_schema(self, generator):
        """Test receivers cover eleven cdevent types with a schema."""
        receivers = generator.generate_event_receivers()
        assert len(receivers) == 11
        assert all("schema" in receiver for receiver in receivers)
        assert len({receiver["type"] for receiver in receivers}) == 11

    def test_events_are_four_services_times_eleven_types(self, generator):
        """Test events are four services times eleven types."""
        events = generator.generate_events({})
        assert len(events) == 44
        assert {event["name"] for event in events} == {"foo", "bar", "baz", "qux"}
        assert all(re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", event["release"]) for event in events)

    def test_events_use_the_receiver_ids_they_are_given(self, generator):
        """Test events use the receiver ids they are given."""
        receivers = {r["type"]: {"data": "01ARZ3NDEKTSV4RRFFQ69G5FAV"} for r in generator.generate_event_receivers()}
        events = generator.generate_events(receivers)
        assert {event["event_receiver_id"] for event in events} == {"01ARZ3NDEKTSV4RRFFQ69G5FAV"}

    def test_curl_command_quotes_the_payload(self, generator):
        """Test curl command quotes the payload."""
        command = generator.make_curl_command({"name": "it's"}, "http://epr/api/v1/events")
        assert command.startswith("curl -sS -X POST")
        assert "http://epr/api/v1/events" in command

    def test_dry_run_prints_55_curl_commands_and_exits_zero(self):
        """Test dry run prints 55 curl commands and exits zero."""
        result = subprocess.run(
            [sys.executable, str(DEMOS / "generate_epr_events.py"), "--dry-run"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, result.stderr
        assert sum(1 for line in result.stdout.splitlines() if line.startswith("curl ")) == 55

    def test_unreachable_epr_exits_nonzero(self, tmp_path):
        """Test unreachable epr exits nonzero."""
        result = subprocess.run(
            [sys.executable, str(DEMOS / "generate_epr_events.py"), "--url", "http://127.0.0.1:9", "--timeout", "1"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=tmp_path,
        )
        assert result.returncode == 1
        assert "Posted 0/44 events successfully" in result.stdout

    def test_write_to_disk_writes_files_and_posts_nothing(self, tmp_path):
        """Test write to disk writes files and posts nothing."""
        result = subprocess.run(
            [sys.executable, str(DEMOS / "generate_epr_events.py"), "--write-to-disk", "--dry-run"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=tmp_path,
        )
        assert result.returncode == 0, result.stderr
        assert len(list((tmp_path / "epr_reports" / "events").glob("*.json"))) == 44
        assert len(list((tmp_path / "epr_reports" / "event_receivers").glob("*.json"))) == 11


class TestClientDemos:
    """Tests for the OpenAPI and MCP client demos."""

    @pytest.mark.parametrize("name", ["openapi_demo", "mcp_client_demo"])
    def test_demo_imports_and_documents_its_usage(self, name):
        """Test demo imports and documents its usage."""
        module = load(name)
        assert "Usage:" in module.__doc__
        assert callable(module.main)

    def test_shorten_truncates_long_text(self):
        """Test shorten truncates long text."""
        module = load("mcp_client_demo")
        assert module.shorten("a  b\nc") == "a b c"
        assert module.shorten("x" * 200, 20) == "x" * 17 + "..."

    @pytest.mark.asyncio
    async def test_call_treats_non_json_text_as_a_failure(self):
        """Test call treats non json text as a failure."""
        module = load("mcp_client_demo")

        class Result:
            def __init__(self):
                self.is_error = False
                self.content = [type("Text", (), {"text": "Connection failed to EPR server"})()]

        class Client:
            async def call_tool(self, *args, **kwargs):
                return Result()

        with pytest.raises(module.DemoError, match="returned an error"):
            await module.call(Client(), "fetch_event", {"id": "x"})
        assert await module.call(Client(), "fetch_event", {"id": "x"}, expect_error=True)


def test_openapi_demo_runs_end_to_end():
    """Starts the real server on a free port; EPR is not contacted."""
    result = subprocess.run(
        [sys.executable, str(DEMOS / "openapi_demo.py")],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "found 9 tools" in result.stdout
    assert "JSON matches the YAML document: True" in result.stdout


def test_demos_do_not_use_the_legacy_httpx_package():
    """Test demos do not use the legacy httpx package."""
    pattern = re.compile(r"^\s*(import httpx|from httpx)\b(?!2)", re.MULTILINE)
    offenders = [str(path) for path in DEMOS.glob("*.py") if pattern.search(path.read_text())]
    assert offenders == []


def test_run_all_script_is_executable_and_valid_bash():
    """Test run all script is executable and valid bash."""
    script = DEMOS / "scripts" / "run_all.sh"
    assert script.stat().st_mode & 0o111
    assert subprocess.run(["bash", "-n", str(script)]).returncode == 0
    refused = subprocess.run([str(script), "--bogus"], capture_output=True, text=True)
    assert refused.returncode == 2


def test_every_demo_has_a_presenter_script():
    """Test every demo has a presenter script."""
    scripts = DEMOS / "scripts"
    for name in ("generate_events_script.md", "openapi_demo_script.md", "mcp_client_demo_script.md"):
        assert (scripts / name).is_file()
    readme = (DEMOS / "README.md").read_text()
    for demo in ("generate_epr_events.py", "openapi_demo.py", "mcp_client_demo.py"):
        assert demo in readme
