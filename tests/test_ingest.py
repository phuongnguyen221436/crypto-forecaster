import importlib
import sys

import pytest


class FakeDuckConnection:
    def __init__(self):
        self.executed = []

    def execute(self, query, *args, **kwargs):
        self.executed.append(query.strip())
        return self


class FakeRedis:
    def __init__(self):
        self.kwargs = None


@pytest.fixture()
def ingest_module(monkeypatch):
    fake_duck = FakeDuckConnection()
    fake_redis = FakeRedis()

    if "ingest.ingest" in sys.modules:
        del sys.modules["ingest.ingest"]

    monkeypatch.setattr("duckdb.connect", lambda path: fake_duck)
    monkeypatch.setattr("redis.Redis", lambda **kwargs: fake_redis)

    module = importlib.import_module("ingest.ingest")
    return module, fake_duck, fake_redis


def test_normalize_trade_buy_side(ingest_module):
    ingest, _, _ = ingest_module

    raw = {"T": 1700000000000, "p": "64000.42", "q": "0.012", "m": False}
    normalized = ingest.normalize_trade(raw)

    assert normalized == {
        "ts": 1700000000000,
        "price": 64000.42,
        "qty": 0.012,
        "side": "buy",
    }


def test_normalize_trade_sell_side(ingest_module):
    ingest, _, _ = ingest_module

    raw = {"T": 1700000000100, "p": "64001.0", "q": "0.5", "m": True}
    normalized = ingest.normalize_trade(raw)

    assert normalized["side"] == "sell"


def test_ingest_initializes_duckdb_schema(ingest_module):
    _, fake_duck, _ = ingest_module

    create_statements = [q for q in fake_duck.executed if q.startswith("CREATE TABLE")]
    assert create_statements, "ingest should create the trades table if missing"
