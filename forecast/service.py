from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
import asyncio
import redis
import json

app = FastAPI()

# connect to redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

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
          ofi = float(fields.get("ofi", 0))
          # send the trade event to the client

          if ofi > 0.2:
            prob_up, prob_down = 0.7, 0.3
          elif ofi < -0.2:
            prob_up, prob_down = 0.3, 0.7
          else:
            prob_up, prob_down = 0.5, 0.5
          
          payload = {
            "id": message_id,
            "ts": int(fields.get("ts", 0)),
            "price": float(fields.get("price", 0)),
            "qty": float(fields.get("qty", 0)),
            "side": fields.get("side", "buy"),
            "ofi": ofi,
            "prob_up": prob_up,
            "prob_down": prob_down,
          }

          await websocket.send_text(json.dumps(payload)) # send the trade event as a JSON string to the client
          last_id = message_id  # update last_id to the ID of the last processed message
  except WebSocketDisconnect:
    return
