import redis
import time

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
STREAM = "trades:btcusdt"

last_id = "0"  # start reading from the beginning of the stream or lastest with "$"

while True:
  # XREAD blocks until a new message arrives
  # COUNT 1 means: read only one message at a time

  events = r.xread({STREAM: last_id}, block=0, count=1) 
  # what is the format of events?
  # events is a list of (stream, [ (id, {field: value}), ... ]) tuples
  # e.g. [ ('trades:btcusdt', [ ('1625247600000-0', {'ts': '1625247600000', 'price': '34000.0', 'qty': '0.001', 'side': 'buy'}) ]) ]

  for stream, messages in events:
    for message_id, fields in messages:
      print(f"Message ID: {message_id}, Field: {fields}") # msg_id = Redis ID, fields = your trade event
      last_id = message_id  # update last_id to the ID of the last processed message