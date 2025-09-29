# Testing Guide

This project has separate suites for the Python backend services and the React dashboard.

## Python (pytest)

Requirements are listed in `requirements.txt`. Install them once, then run the tests from the repo root:

```bash
python3 -m pip install -r requirements.txt
pytest
```

Key coverage:
- `tests/test_ingest.py` validates `normalize_trade` and ensures the DuckDB schema is created without touching external services.
- `tests/test_replay.py` confirms `ingest/replay.py` streams stringified events to Redis.
- `tests/test_service.py` spins up the FastAPI app with a fake Redis client and verifies that the `/ws/trades` websocket yields normalized payloads.

All external dependencies (Redis, DuckDB connections) are faked, so the suite runs offline.

## React Dashboard (Vitest)

Install dashboard dependencies once:

```bash
cd dashboard
npm install
```

Run the component tests with:

```bash
npm run test
```

Vitest is configured in `dashboard/vite.config.ts` to use jsdom and the setup file at `dashboard/src/test/setup.ts`. Current tests live under `dashboard/src/components/__tests__/` and cover:
- `PriceTicker` rendering of price/status and error states.
- `TradeFeed` ordering of recent trades and the empty-state placeholder.

Add new component tests next to the components they exercise so Vitest picks them up automatically.
