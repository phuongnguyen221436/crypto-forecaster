import importlib
import sys

import pytest
from fastapi.testclient import TestClient


class FakeRedis:
    def __init__(self, batches):
        self.batches = batches
        self.xread_calls = []

    def xread(self, *args, **kwargs):
        self.xread_calls.append((args, kwargs))
        if self.batches:
            return self.batches.pop(0)
        return []


@pytest.fixture()
def service_client(monkeypatch):
    events = [
        [
            (
                "trades:btcusdt",
                [
                    (
                        "1-0",
                        {"ts": "1700000000000", "price": "64000.0", "qty": "0.01", "side": "buy"},
                    )
                ],
            )
        ]
    ]

    fake_redis = FakeRedis(events)

    if "forecast.service" in sys.modules:
        del sys.modules["forecast.service"]

    monkeypatch.setattr("redis.Redis", lambda **kwargs: fake_redis)

    service = importlib.import_module("forecast.service")
    service.r = fake_redis

    client = TestClient(service.app)
    return client, fake_redis


def test_websocket_emits_normalized_payload(service_client):
    client, _ = service_client

    with client.websocket_connect("/ws/trades") as websocket:
        message = websocket.receive_json()

    assert message["id"] == "1-0"
    assert message["ts"] == 1700000000000
    assert message["price"] == 64000.0
    assert message["qty"] == 0.01
    assert message["side"] == "buy"

    # allow extra enrichment fields while ensuring numeric types
    if "prob_up" in message:
        assert isinstance(message["prob_up"], (int, float))
        assert 0.0 <= message["prob_up"] <= 1.0
    if "prob_down" in message:
        assert isinstance(message["prob_down"], (int, float))
        assert 0.0 <= message["prob_down"] <= 1.0
    if "ofi" in message:
        assert isinstance(message["ofi"], (int, float))
    assert message.get("predictor") in {"model", "heuristic"}
