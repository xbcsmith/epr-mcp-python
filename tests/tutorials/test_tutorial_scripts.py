# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for the workshop's helper scripts: seed_epr.py, check_setup.py, and client.py."""

import importlib.util
import json
import sys
from pathlib import Path

import httpx2
import pytest  # type: ignore

CODE = Path(__file__).resolve().parents[2] / "docs" / "tutorials" / "code"


def load(name: str):
    """Import a script from the workshop code directory as a module."""
    spec = importlib.util.spec_from_file_location(f"workshop_{name}", CODE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSeedEpr:
    """Tests for seed_epr.py."""

    def test_create_returns_the_new_id(self):
        """Test create returns the new id."""
        seed = load("seed_epr")
        transport = httpx2.MockTransport(lambda request: httpx2.Response(200, json={"data": "01ABC"}))
        with httpx2.Client(base_url="http://epr.test", transport=transport) as client:
            assert seed.create(client, "/api/v1/receivers", {"name": "x"}) == "01ABC"

    def test_create_raises_on_an_error_status(self):
        """Test create raises on an error status."""
        seed = load("seed_epr")
        transport = httpx2.MockTransport(lambda request: httpx2.Response(400, text="bad"))
        with httpx2.Client(base_url="http://epr.test", transport=transport) as client:
            with pytest.raises(httpx2.HTTPStatusError):
                seed.create(client, "/api/v1/receivers", {})

    def test_main_saves_ids_and_exits_zero(self, tmp_path, monkeypatch, capsys):
        """Test main saves ids and exits zero."""
        seed = load("seed_epr")
        counter = iter(range(100))
        transport = httpx2.MockTransport(lambda request: httpx2.Response(200, json={"data": f"ID{next(counter)}"}))
        real_client = httpx2.Client
        monkeypatch.setattr(seed.httpx2, "Client", lambda **kw: real_client(transport=transport, **kw))
        monkeypatch.setattr(seed, "IDS_FILE", tmp_path / "ids.json")
        assert seed.main() == 0
        ids = json.loads((tmp_path / "ids.json").read_text())
        assert ids["receiver_id"] == "ID0" and len(ids["event_ids"]) == 3
        assert "Saved to" in capsys.readouterr().out

    def test_main_reports_an_unreachable_epr(self, monkeypatch, capsys):
        """Test main reports an unreachable epr."""
        seed = load("seed_epr")

        def refuse(**kwargs):
            raise httpx2.ConnectError("refused")

        monkeypatch.setattr(seed.httpx2, "Client", refuse)
        assert seed.main() == 1
        assert "Cannot reach EPR" in capsys.readouterr().err


class TestCheckSetup:
    """Tests for check_setup.py."""

    def test_report_counts_only_failures(self, capsys):
        """Test report counts only failures."""
        check = load("check_setup")
        check.report("PASS", "a")
        check.report("SKIP", "b", "later")
        assert check.failures == 0
        check.report("FAIL", "c", "broken")
        assert check.failures == 1
        out = capsys.readouterr().out
        assert "PASS" in out and "FAIL" in out and "broken" in out

    def test_check_epr_passes_when_ready_and_fails_when_down(self, monkeypatch, capsys):
        """Test check epr passes when ready and fails when down."""
        check = load("check_setup")
        monkeypatch.setattr(check.httpx2, "get", lambda url, timeout: httpx2.Response(200))
        check.check_epr()
        assert check.failures == 0

        def down(url, timeout):
            raise httpx2.ConnectError("refused")

        monkeypatch.setattr(check.httpx2, "get", down)
        check.check_epr()
        assert check.failures == 1
        assert "docker compose up" in capsys.readouterr().out

    def test_check_python_passes_on_this_interpreter(self):
        """Test check python passes on this interpreter."""
        check = load("check_setup")
        check.check_python()
        assert check.failures == 0

    def test_check_uv_reports_a_missing_uv(self, monkeypatch):
        """Test check uv reports a missing uv."""
        check = load("check_setup")
        monkeypatch.setattr(check.shutil, "which", lambda name: None)
        assert check.check_uv() is None
        assert check.failures == 1

    def test_main_returns_one_when_a_check_fails(self, monkeypatch):
        """Test main returns one when a check fails."""
        check = load("check_setup")
        monkeypatch.setattr(sys, "argv", ["check_setup.py", "--skip-stdio"])
        monkeypatch.setattr(check, "check_uv", lambda: None)
        monkeypatch.setattr(check, "check_epr", lambda: check.report("FAIL", "EPR"))
        monkeypatch.setattr(check, "check_in_process", lambda: None)
        assert check.main() == 1


class TestClient:
    """Tests for client.py."""

    @pytest.mark.asyncio
    async def test_list_prints_the_tools(self, capfd):
        """Test list prints the tools."""
        client = load("client")
        status = await client.run(CODE / "checkpoint_01_first_tool" / "server.py", None, {})
        assert status == 0
        assert "fetch_event" in capfd.readouterr().out

    @pytest.mark.asyncio
    async def test_call_with_invalid_arguments_returns_one(self, capfd):
        """Test call with invalid arguments returns one."""
        client = load("client")
        status = await client.run(CODE / "checkpoint_04_validation" / "server.py", "fetch_event", {"id": "bad"})
        assert status == 1
