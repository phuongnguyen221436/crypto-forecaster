import importlib
import sys

import pytest


class FakeDuckCursor:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows


class FakeDuckConnection:
    def __init__(self, rows):
        self.rows = rows
        self.last_query = None

    def execute(self, query, params):
        self.last_query = (query.strip(), params)
        return FakeDuckCursor(self.rows)


class FakeRedis:
    def __init__(self):
        self.events = []

    def xadd(self, name, fields):
        self.events.append((name, fields))
        return "0-1"


@pytest.fixture()
def replay_module(monkeypatch):
    rows = [
        (1700000000000, 64000.0, 0.01, "buy"),
        (1700000001000, 64010.0, 0.015, "sell"),
    ]

    fake_con = FakeDuckConnection(rows)
    fake_redis = FakeRedis()

    if "ingest.replay" in sys.modules:
        del sys.modules["ingest.replay"]

    monkeypatch.setattr("duckdb.connect", lambda path: fake_con)
    monkeypatch.setattr("redis.Redis", lambda **kwargs: fake_redis)

    module = importlib.import_module("ingest.replay")
    module.con = fake_con
    module.r = fake_redis

    return module, fake_con, fake_redis


def test_replay_pushes_events_as_strings(replay_module):
    replay, fake_con, fake_redis = replay_module

    replay.replay(1700000000000, 1700000005000, delay=0)

    # ensure query executed with passed params
    query, params = fake_con.last_query
    assert "BETWEEN ? AND ?" in query
    assert params == [1700000000000, 1700000005000]

    # redis should receive stringified fields
    assert fake_redis.events
    _, fields = fake_redis.events[0]
    assert fields == {
        "ts": "1700000000000",
        "price": "64000.0",
        "qty": "0.01",
        "side": "buy",
    }
