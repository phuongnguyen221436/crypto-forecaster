from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
import asyncio
import redis
import json

from processor.predictor import PriceDirectionPredictor

app = FastAPI()

# connect to redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
predictor = PriceDirectionPredictor()

@app.websocket("/ws/trades") # define a websocket endpoint at /ws/trades
async def websocket_trades(websocket: WebSocket):
  await websocket.accept() # accept the websocket connection
  last_id = "0"  # start reading from the beginning of the stream or lastest with "$"

  try:
    while True:
      # read new trades from redis stream; returns None if nothing arrived within block window
      events = r.xread({"trades:btcusdt": last_id}, block=1000, count=10) # block=1000 means: wait up to 1000ms for new messages, count=10 means: read up to 10 messages at a time

      if not events:
        await asyncio.sleep(0)  # yield control to event loop to avoid busy waiting
        continue

      for stream, messages in events:
        for message_id, fields in messages:
          ts = int(fields.get("ts", 0))
          raw_qty = float(fields.get("qty", 0))
          side = fields.get("side", "buy")
          price = float(fields.get("price", 0))
          ofi = float(fields.get("ofi", 0))
          if ofi == 0:
            ofi = raw_qty if side == "buy" else -raw_qty

          prob_up, prob_down, source = predictor.predict(
            {"qty": raw_qty, "side": side, "price": price, "ofi": ofi}
          )

          payload = {
            "id": message_id,
            "ts": ts,
            "price": price,
            "qty": raw_qty,
            "side": side,
            "ofi": ofi,
            "prob_up": prob_up,
            "prob_down": prob_down,
            "predictor": source,
          }

          await websocket.send_text(json.dumps(payload)) # send the trade event as a JSON string to the client
          last_id = message_id  # update last_id to the ID of the last processed message
  except WebSocketDisconnect:
    return
