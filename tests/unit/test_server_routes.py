"""Tests for the HTTP routes served next to the MCP endpoint."""

from pathlib import Path

import pytest  # type: ignore
import yaml
from starlette.testclient import TestClient

from epr_mcp import server
from epr_mcp.config import Config


@pytest.fixture
def client():
    mcp = server.create_server(Config(url="http://epr.test"))
    with TestClient(mcp.http_app()) as test_client:
        yield test_client


class TestRoutes:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.text == "OK"

    def test_openapi_yaml(self, client):
        response = client.get("/openapi.yaml")
        assert response.status_code == 200
        assert yaml.safe_load(response.text)["openapi"].startswith("3.")

    def test_openapi_json_matches_yaml(self, client):
        spec = client.get("/openapi.json").json()
        assert spec == yaml.safe_load(client.get("/openapi.yaml").text)

    def test_docs_points_at_openapi_json(self, client):
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger-ui" in response.text
        assert "/openapi.json" in response.text

    def test_missing_spec_returns_404(self, client, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda self: False)
        assert client.get("/openapi.yaml").status_code == 404
        assert client.get("/openapi.json").status_code == 404


def test_openapi_spec_is_package_data():
    """The spec must sit inside the package so the wheel can ship it."""
    spec = Path(server.__file__).parent / "openapi.yaml"
    assert spec.is_file()


def test_pyproject_ships_openapi_spec():
    """The build configuration must include the spec in the wheel."""
    import tomllib

    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    config = tomllib.loads(pyproject.read_text())
    assert "openapi.yaml" in config["tool"]["setuptools"]["package-data"]["epr_mcp"]
