import asyncio
import websockets
import json
import argparse
import time
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

# Define the WebSocket server URIs
receive_uris = {
    "binance": ["wss://stream.binance.com:9443/ws/ethusdt@trade",
                "wss://stream.binance.com:9443/ws/btcusdt@trade",
                "wss://stream.binance.com:9443/ws/uniusdt@trade",
                "wss://stream.binance.com:9443/ws/shibusdt@trade",
                "wss://stream.binance.com:9443/ws/arbusdt@trade",
                "wss://stream.binance.com:9443/ws/bnbusdt@trade",
                "wss://stream.binance.com:9443/ws/solusdt@trade",
                "wss://stream.binance.com:9443/ws/linkusdt@trade",
                ]
}

send_uri = os.getenv('URL_WEBSOCKET_SERVER_AWS')

# Initialize a session using Amazon DynamoDB
dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('yourtablenameevent')

def mapping_ticker_binance(ticker):
    mapping ={
        "ETHUSDT": "ETH",
        "BTCUSDT": "BTC",
        "UNIUSDT": "UNI",
        "SHIBUSDT": "SHIB",
        "ARBUSDT": "ARB",
        "SOLUSDT": "SOL",
        "BNBUSDT": "BNB",
        "LINKUSDT": "LINK",
    }
    return mapping[ticker]

def format_binance_message(message):
    message = json.loads(message)
    price = f"{round(float(message['p']), 2):.2f}" if float(message['p']) > 1 else f"{round(float(message['p']), 8):.8f}"
    ticker = mapping_ticker_binance(message["s"])
    send_message = {
        "ticker#network": f"{ticker}#CEX", 
        "exchange": "binance",
        "price": price,
        "is_eth": False, 
        "timestamp": int(time.time())
    }
    return send_message

def format_send_message_websocket_server(message):
    if args.exchange=="binance":
        message = format_binance_message(message)
    return message

async def send_message_to_dynamodb(message):
    try:
        table.put_item(Item=message)
    except Exception as e:
        print(f"Error: {e}")

async def receive_and_send_data(receive_uri, send_uri):
    while True:
        try:
            async with websockets.connect(receive_uri, ping_interval=2, ping_timeout=None) as receive_ws:
                async with websockets.connect(send_uri, ping_interval=2, ping_timeout=None) as send_ws:
                    while True:
                        message = await receive_ws.recv()
                        _format_message = format_send_message_websocket_server(message)
                        await send_ws.send(json.dumps({'action': 'SendMessage', 'message': json.dumps(_format_message)}))
                        await send_message_to_dynamodb(_format_message)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(10)

async def main(receive_uri, send_uri):
    tasks = [receive_and_send_data(uri, send_uri) for uri in receive_uri]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebSocket client for receiving and sending data.")
    parser.add_argument("-e","--exchange", type=str, required=False, help="Exchange")
    args = parser.parse_args()
    asyncio.run(main(receive_uris[args.exchange], send_uri))