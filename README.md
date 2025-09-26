# Crypto Impact Forecaster

## 1. Overview

This project implements a real-time infrastructure system for streaming, processing, and forecasting cryptocurrency trades. It ingests tick-level market data from Binance, processes it into rolling market features, and generates forecasts on short-term price movement.

The system is designed with the following goals:

* **Low latency**: process thousands of ticks/sec with sub-50ms forecast latency.
* **Determinism**: identical results in live and replay modes.
* **Observability**: throughput, latency, and accuracy are measurable.
* **Extensibility**: feature engineering and forecasting logic can evolve independently.

---

## 2. Architecture

```
Binance WebSocket (trades + order book)
         │
         ▼
 Ingestion (Python, asyncio)
  - Normalizes trade events
  - Pushes to Redis Streams
  - Appends to DuckDB
         │
         ▼
 Redis Stream: trades:btcusdt
         │
   ┌─────┼─────────────────┐
   │     │                 │
Consumer (logger)   Processor (features)   Replay engine
                          │
                          ▼
                 Redis Stream: features:btcusdt
                          │
                          ▼
                 Forecast Service (FastAPI)
                          │
                          ▼
                WebSocket API for UI / clients
```

---

## 3. Components

### 3.1 Market Data Source

* **Binance WebSocket API** (public, no auth).
* Channels used:

  * `btcusdt@trade` → trade ticks.
  * `btcusdt@depth@100ms` → order book updates (for later).

### 3.2 Ingestion Gateway

* Python `asyncio` + `websockets` client.
* Normalizes trade payloads into schema:

  ```json
  {
    "ts": 1695929200000,
    "price": 26120.5,
    "qty": 0.02,
    "side": "buy"
  }
  ```
* Writes each event to:

  * **Redis Streams** for real-time fan-out.
  * **DuckDB** append-only table for persistence and replay.

### 3.3 Event Storage

* **Redis Streams**: real-time event log, enables multiple independent consumers.
* **DuckDB**: append-only database for historical storage and deterministic replay.

### 3.4 Replay Engine

* Reads historical trades from DuckDB.
* Replays them into Redis tick-by-tick with optional delay.
* Guarantees deterministic equivalence between live and replay.

### 3.5 Stream Processor

* Consumes trades from Redis.
* Maintains a rolling window of recent trades.
* Computes features such as:

  * **Order Flow Imbalance (OFI)** = (buys − sells) / total trades.
  * Rolling volatility (planned).
  * Spread / depth imbalance (planned).
* Publishes features into `features:btcusdt` stream.

### 3.6 Forecast Service

* Stateless FastAPI service.
* Consumes feature vectors, outputs probability forecast:

  ```json
  {"ts": 1695929201000, "prob_up": 0.65, "prob_down": 0.35}
  ```
* Current implementation uses heuristics (OFI threshold).
* Future versions may load a trained ML model.

### 3.7 Observability (planned)

* Expose Prometheus metrics for:

  * Ingestion throughput (ticks/sec).
  * Forecast latency (p50, p95).
  * Replay divergence.
  * Forecast accuracy.
* Grafana dashboards for visualization.

---

## 4. Data Flow

1. **Ingestion** pulls trades from Binance and normalizes.
2. Events are written to Redis and DuckDB.
3. **Processor** consumes from Redis, computes features, and emits to `features` stream.
4. **Forecast service** consumes features and publishes probability forecasts.
5. **Replay engine** enables deterministic reprocessing of historical data.
6. External UIs or dashboards consume data via WebSocket API.

---

## 5. Tech Stack

* **Python**: asyncio, websockets, redis-py, duckdb, FastAPI.
* **Redis Streams**: event bus for fan-out.
* **DuckDB**: append-only historical store.
* **FastAPI**: forecast service and WebSocket API.
* **Prometheus + Grafana**: observability (planned).
* **React/Next.js**: frontend (planned).

---

## 6. Roadmap

* [x] Ingestion from Binance.
* [x] Redis fan-out.
* [x] DuckDB persistence.
* [x] Replay engine.
* [x] OFI processor.
* [x] Forecast service (heuristic).
* [ ] Volatility and spread features.
* [ ] ML forecaster (logistic regression or LSTM).
* [ ] Prometheus + Grafana integration.
* [ ] Web dashboard.
