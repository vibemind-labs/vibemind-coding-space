"""ENGINE_API_NUR_LESEN and ENGINE_OUTPUT_BASE: both off/unchanged by default."""
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api import main as api_main
from src.api.routes import dashboard


def _client() -> TestClient:
    app = FastAPI()
    app.middleware("http")(api_main.read_only_switch)

    @app.get("/x")
    def lesen():
        return {"ok": True}

    @app.post("/x")
    def schreiben():
        return {"ok": True}

    return TestClient(app)


def test_read_only_off_by_default(monkeypatch):
    monkeypatch.delenv("ENGINE_API_NUR_LESEN", raising=False)
    assert api_main.api_read_only() is False
    assert _client().post("/x").status_code == 200


@pytest.mark.parametrize("wert", ["1", "true", "ja"])
def test_read_only_refuses_writes_but_not_reads(monkeypatch, wert):
    monkeypatch.setenv("ENGINE_API_NUR_LESEN", wert)
    client = _client()
    assert client.get("/x").status_code == 200
    antwort = client.post("/x")
    assert antwort.status_code == 403 and antwort.json()["detail"] == "read_only"
    assert client.delete("/x").status_code == 403


def test_output_base_default_and_override(monkeypatch, tmp_path):
    monkeypatch.delenv("ENGINE_OUTPUT_BASE", raising=False)
    assert dashboard.output_base_dir() == Path("/app/output")
    monkeypatch.setenv("ENGINE_OUTPUT_BASE", str(tmp_path))
    assert dashboard.output_base_dir() == tmp_path
