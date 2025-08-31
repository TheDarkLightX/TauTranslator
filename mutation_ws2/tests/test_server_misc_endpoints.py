from __future__ import annotations

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed in test environment")
from fastapi.testclient import TestClient
from backend.api.server import app


client = TestClient(app)


def test_health_endpoints_and_root_headers():
    r1 = client.get("/healthz")
    assert r1.status_code == 200
    assert r1.json().get("status") == "ok"
    assert r1.headers.get("X-Request-ID")
    assert r1.headers.get("X-Response-Time")

    r2 = client.get("/health")
    assert r2.status_code == 200
    assert r2.json().get("status") == "ok"
    assert r2.headers.get("X-Request-ID")
    assert r2.headers.get("X-Response-Time")

    r3 = client.get("/")
    assert r3.status_code == 200
    body = r3.json()
    assert body.get("status") == "ok"
    assert body.get("name")
    assert body.get("openapi") == "/openapi.json"


def test_cors_preflight_always_ok():
    r = client.options("/any/random/path")
    assert r.status_code == 200

