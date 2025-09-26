import redis
import duckdb
import time

# connect to Redis (running in Docker on localhost:6379)
r = redis.Redis(host="localhost",port=6379,decode_responses=True)
STREAM = "trades:btcusdt"

# connect to duckdb
con = duckdb.connect("storage/trades.db")

def replay(start_ts, end_ts, delay=0.05): # explain
  """
  Replay trades between [start_ts, end_ts] into redis
  delay = sleep between trades, in seconds, to simulate real-time ingestion
  """

  row = con.execute("""
  SELECT ts, price, qty, side FROM trades
                    WHERE ts BETWEEN ? AND ?
                    ORDER BY ts
                    """, [start_ts, end_ts]).fetchall()
  
  for ts, price, qty, side in row:
    event = {
      "ts": int(ts),
      "price": float(price),
      "qty": float(qty),
      "side": side,
    }

    # redis streams store string values; convert to str while keeping JSON-friendly types
    r.xadd(STREAM, {k: str(v) for k, v in event.items()})
    print("[Replay]", event)
    time.sleep(delay) # wait a bit before sending the next trade, to simulate real-time


if __name__ == "__main__":
  # Ex: replay the last 1 min of trades
  now = int(time.time() * 1000) # current time in ms
  one_min_ago = now - 60_000
  replay(one_min_ago, now) # replay last 1 min of trades
