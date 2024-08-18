import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

url_websocket_server = os.getenv('URL_WEBSOCKET_SERVER_AWS')

MESSAGE = {'action': 'SendMessage', 'message': '{"ticker":"ETH", "network":"mainnet","binance": 100000000, "timestamp": 223232323, "timeframe_1M": -0.1, "timeframe_5M": -0.2, "timeframe_30M": 1, "timeframe_1H": 1.2, "timeframe_6H": 1.1, "timeframe_24H": 1.2}'}

async def send_message():
    uri = url_websocket_server
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(MESSAGE))
        print(f"Sent message to server: {MESSAGE}")
        response = await websocket.recv()
        print(f"Received response from server: {MESSAGE}")

if __name__ == "__main__":
    asyncio.run(send_message())