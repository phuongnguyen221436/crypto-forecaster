import redis
from collections import deque

# connect to Redis (running in Docker on localhost:6379)
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

TRADE_STREAM = "trades:btcusdt"  # name of the Redis stream to read trades from
FEATURE_STREAM = "features:btcusdt"  # name of the Redis stream to write features to

WINDOW_SIZE = 100 # keep the last 100 trades in memory for feature calculation
trades_window = deque(maxlen=WINDOW_SIZE) # deque is a double-ended queue that can be used as a sliding window

last_id = "0"  # start reading from the beginning of the stream or lastest with "$"

while True:
  # read 1 new event at a time
  events = r.xread({TRADE_STREAM: last_id}, block=0, count=1)

  for stream, messages in events:
    for message_id, fields in messages:
      # convert fields from strings to appropriate types
      ts = int(fields.get("ts", 0))
      price = float(fields.get("price", 0))
      qty = float(fields.get("qty", 0))
      side = fields.get("side", "buy")

      # add the new trade to the sliding window
      trades_window.append(side)

      buys = trades_window.count("buy")
      sells = trades_window.count("sell")
      total = buys + sells if (buys + sells) > 0 else 1 # avoid division by zero
      ofi = (buys - sells) / total # order flow imbalance is the normalized difference between buy and sell trades, used as a simple feature to predict short-term price movements
      features = {"ts": ts, "ofi": ofi}

      # print for now
      print(features)

      # (later) push features into Redis for forecast service
      r.xadd(FEATURE_STREAM, features)

      # update last_id so we don’t re-read old events
      last_id = message_id



     