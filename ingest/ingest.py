import asyncio
import websockets # use this to connect to Binance API
import json # use this to parse JSON messages into Python dictionaries
import redis
import duckdb # store trades in a local DuckDB database
import sys
# connect to Redis (running in Docker on localhost:6379) 
r = redis.Redis(host='localhost', port=6379, decode_responses=True) 
REDIS_STREAM = "trades:btcusdt" # name of the Redis stream to store trades

# connect to DuckDB (creates trades.db file if it doesn't exist)
try: 
  con = duckdb.connect('storage/trades.db')
  # append only schema: one row per trade
  con.execute("""
  CREATE TABLE IF NOT EXISTS trades (
      ts BIGINT,
      price DOUBLE,
      qty DOUBLE,
      side VARCHAR
  );
  """)
except duckdb.IOException as e:
    print("❌ Could not open DuckDB database. It may already be locked by another process.")
    print("💡 Tip: close other DuckDB shells or kill processes using it.")
    print("🔎 Error details:", e)
    sys.exit(1)   # exit cleanly



async def consume_trades(): # this function will connect to Binance's trade stream and keep reading messages
    # "btcusdt@trade" means: send me every trade that happens on the BTC/USDT pair
    url = "wss://stream.binance.com:9443/ws/btcusdt@trade"

    # connect to the websocket server at Binance and keep the connection open
    # async with means: wait for the connection to be established before proceeding, open automatically, close it when done
    async with websockets.connect(url) as websocket:
        # loop forever, reading messages as they come in
        # async for means: wait for the next message without blocking other tasks
        async for message in websocket:
            # print the raw JSON message received from Binance
            # at this point, message is just a JSON string
            raw = json.loads(message)
            event = normalize_trade(raw) # normalize the trade data into clean schema

            r.xadd(REDIS_STREAM, event) # add the normalized trade data to the Redis stream

            # write to duckdb
            con.execute("INSERT INTO trades VALUES (?, ?, ?, ?)", (event["ts"], event["price"], event["qty"], event["side"]))




            print(event) # print the normalized trade data
           
            # in a real application, you would parse the JSON and store it in a database or process it further
            # for example:
            # trade = json.loads(message)
            # store_trade_in_db(trade)

def normalize_trade(raw):
    """
    Convert Binance's raw trade message into our clean schema.
    raw: the original dict from Binance
    return: dict with fields (ts, price, qty, side)
    """
    event = {
        "ts": raw["T"], # trade time
        "price": float(raw["p"]), # price as float
        "qty": float(raw["q"]), # quantity as float
        "side": "buy" if raw["m"] == False else "sell" # if "m" is false, buyer is the market maker, so it's a buy; otherwise it's a sell
    }
    return event

    
if __name__ == "__main__":
    # run the consume_trades coroutine until it completes (which it never will in this case)
    asyncio.run(consume_trades())




