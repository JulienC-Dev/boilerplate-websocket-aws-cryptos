"""
CMD example: 
brownie networks add Ethereum ethereum-mainnet host=https://eth-mainnet.g.alchemy.com/v2/$WEB3_ALCHEMY_PROJECT_ID_ETH_MAINNET chainid=1
brownie run scripts/defi/websocket_client_defi.py --network=ethereum-mainnet
brownie run scripts/defi/websocket_client_defi.py --network=arbitrum-mainnet
brownie run scripts/defi/websocket_client_defi.py --network=optimism-mainnet
brownie run scripts/defi/websocket_client_defi.py --network=base-mainnet
brownie run scripts/defi/websocket_client_defi.py --network=polygon-mainnet
"""
from brownie import config, network
import asyncio
import websockets
import json
import time
import os
from dotenv import load_dotenv
import boto3

load_dotenv()

# Define the WebSocket to listen depending on the networks
receive_uris = {
    "ethereum-mainnet": [os.getenv('WEB3_ALCHEMY_PROJECT_ID_ETH_MAINNET'),
    ],
    "arbitrum-mainnet": [os.getenv('WEB3_ALCHEMY_PROJECT_ID_ARBITRUM_MAINNET'),
                ],
    "optimism-mainnet": [os.getenv('WEB3_ALCHEMY_PROJECT_ID_OPTIMISM_MAIN'),
                ],
    "base-mainnet": [os.getenv('WEB3_ALCHEMY_PROJECT_ID_BASE_MAINNET'),
                ],
    "polygon-mainnet": [os.getenv('WEB3_ALCHEMY_PROJECT_ID_POLYGON_MAINNET'),
                ],
}

send_uri = os.getenv('URL_WEBSOCKET_SERVER_AWS')  # Replace with your send server URI

MAPPING_ADRESS_TICKER = {
    "arbitrum-mainnet" : 
    {
        "0x82af49447d8a07e3bd95bd0d56f35241523fbab1": "ETH",
        "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8": "USDC",
        "0xfa7f8980b0f1e64a2062791cc3b0871572f1f7f0": "UNI",
        "0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a": "GMX",
        "0x912ce59144191c1204e64559fe8253a0e49e6548": "ARB",
        "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f": "BTC",
    }
    ,
    "ethereum-mainnet" : {
        "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": "ETH",
        "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": "USDC",
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984": "UNI",
        "0x514910771af9ca656af840dff83e8264ecf986ca": "LINK",
        "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599": "BTC",
    },
    "optimism-mainnet" : {
        "0x4200000000000000000000000000000000000006": "ETH",
        "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85": "USDC",
        "0x68f180fcce6836688e9084f035309e29bf0a2095": "BTC",
        "0x4200000000000000000000000000000000000042": "OP",
        "0x7f5c764cbc14f9669b88837ca1490cca17c31607": "USDC"
    },
    "base-mainnet" : {
        "0x4200000000000000000000000000000000000006": "ETH",
        "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913": "USDC",
    },
    "polygon-mainnet" : {
        "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619": "ETH",
        "0x2791bca1f2de4661ed88a30c99a7a9449aa84174": "USDC",
        "0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6": "BTC",
        "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270": "MATIC",
        "0x53e0bca35ec356bd5dddfebbd1fc0fd03fabad39": "LINK",
    },
}

# You can add more protocol: pancakeswap, curve
MAPPING_POOL_PROTOCOLE = {
    "0xc31e54c7a869b9fcbecc14363cf510d1c41fa443": "uniswap", 
    "0xc24f7d8e51a64dc1238880bd00bb961d54cbeb29": "uniswap",
    "0x1aeedd3727a6431b8f070c0afaa81cc74f273882": "uniswap", 
    "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8": "uniswap",
    "0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801": "uniswap",
    "0xa6cc3c2531fdaa6ae1a3ca84c2855806728693e8": "uniswap",
    "0x99ac8ca7087fa4a2a1fb6357269965a2014abc35": "uniswap",
    "0x1fb3cf6e48f1e7b10213e7b6d87d4c073c7fdb7b": "uniswap",
    "0xfad57d2039c21811c8f2b5d5b65308aa99d31559": "uniswap",
    "0xd0fc8ba7e267f2bc56044a7715a489d851dc6d78": "uniswap",
    "0xcda53b1f66614552f834ceef361a8d12a0b8dad8": "uniswap",
    "0xac70bd92f89e6739b3a08db9b6081a923912f73d": "uniswap",
    "0xbed2589fefae17d62a8a4fdac92fa5895cae90d2": "uniswap",
    "0xa7bb0d95c6ba0ed0aca70c503b34bc7108589a47": "uniswap",
    "0x1c3140ab59d6caf9fa7459c6f83d4b52ba881d36": "uniswap",
    "0xd0b53d9277642d899df5c87a3966a349a798f224": "uniswap",
    "0x45dda9cb7c25131df268515131f647d726f50608": "uniswap",
    "0xeef1a9507b3d505f0062f2be9453981255b503c8": "uniswap",
    "0xa374094527e1673a86de625aa59517c5de346d32": "uniswap",
    "0x94ab9e4553ffb839431e37cc79ba8905f45bfbea": "uniswap",
}

EVENT_TYPE = {
    "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67": "swap_event"
}

# first item is token0 and second item is token1
POOL_TOKENS_ADDRESS = {
    "0xc31e54c7a869b9fcbecc14363cf510d1c41fa443": ["0x82af49447d8a07e3bd95bd0d56f35241523fbab1", "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8"], 
    "0xc24f7d8e51a64dc1238880bd00bb961d54cbeb29": ["0x82af49447d8a07e3bd95bd0d56f35241523fbab1", "0xfa7f8980b0f1e64a2062791cc3b0871572f1f7f0"],
    "0x1aeedd3727a6431b8f070c0afaa81cc74f273882": ["0x82af49447d8a07e3bd95bd0d56f35241523fbab1", "0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a"], 
    "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8": ["0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"],
    "0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801": ["0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"],
    "0xa6cc3c2531fdaa6ae1a3ca84c2855806728693e8": ["0x514910771af9ca656af840dff83e8264ecf986ca", "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"],
    "0x99ac8ca7087fa4a2a1fb6357269965a2014abc35": ["0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"],
    "0x1fb3cf6e48f1e7b10213e7b6d87d4c073c7fdb7b": ["0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85", "0x4200000000000000000000000000000000000006"],
    "0xfad57d2039c21811c8f2b5d5b65308aa99d31559": ["0x514910771af9ca656af840dff83e8264ecf986ca", "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"],
    "0xd0fc8ba7e267f2bc56044a7715a489d851dc6d78": ["0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"],
    "0xcda53b1f66614552f834ceef361a8d12a0b8dad8": ["0x912ce59144191c1204e64559fe8253a0e49e6548", "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8"],
    "0xac70bd92f89e6739b3a08db9b6081a923912f73d": ["0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f", "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8"],
    "0xbed2589fefae17d62a8a4fdac92fa5895cae90d2": ["0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a", "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8"],
    "0xa7bb0d95c6ba0ed0aca70c503b34bc7108589a47": ["0x68f180fcce6836688e9084f035309e29bf0a2095", "0x7f5c764cbc14f9669b88837ca1490cca17c31607"],
    "0x1c3140ab59d6caf9fa7459c6f83d4b52ba881d36": ["0x4200000000000000000000000000000000000042", "0x7f5c764cbc14f9669b88837ca1490cca17c31607"],
    "0xd0b53d9277642d899df5c87a3966a349a798f224": ["0x4200000000000000000000000000000000000006", "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"],
    "0x45dda9cb7c25131df268515131f647d726f50608": ["0x2791bca1f2de4661ed88a30c99a7a9449aa84174", "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619"],
    "0xeef1a9507b3d505f0062f2be9453981255b503c8": ["0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6", "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"],
    "0xa374094527e1673a86de625aa59517c5de346d32": ["0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270", "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"],
    "0x94ab9e4553ffb839431e37cc79ba8905f45bfbea": ["0x2791bca1f2de4661ed88a30c99a7a9449aa84174", "0x53e0bca35ec356bd5dddfebbd1fc0fd03fabad39"]
}

POOL_DECIMAL_PRICE = {
    "0xc31e54c7a869b9fcbecc14363cf510d1c41fa443": 10 ** 12, 
    "0xc24f7d8e51a64dc1238880bd00bb961d54cbeb29": 0,
    "0x1aeedd3727a6431b8f070c0afaa81cc74f273882": 0,
    "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8": 10 ** 12,
    "0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801": 0,
    "0xa6cc3c2531fdaa6ae1a3ca84c2855806728693e8": 0,
    "0x99ac8ca7087fa4a2a1fb6357269965a2014abc35": 10 ** 2,
    "0x1fb3cf6e48f1e7b10213e7b6d87d4c073c7fdb7b": 10 ** 12,
    "0xfad57d2039c21811c8f2b5d5b65308aa99d31559": 10 ** 12,
    "0xd0fc8ba7e267f2bc56044a7715a489d851dc6d78": 10 ** 12,
    "0xcda53b1f66614552f834ceef361a8d12a0b8dad8": 10 ** 12,
    "0xac70bd92f89e6739b3a08db9b6081a923912f73d": 10 ** 2,
    "0xbed2589fefae17d62a8a4fdac92fa5895cae90d2": 10 ** 12,
    "0xa7bb0d95c6ba0ed0aca70c503b34bc7108589a47": 10 ** 2,
    "0x1c3140ab59d6caf9fa7459c6f83d4b52ba881d36": 10 ** 12,
    "0xd0b53d9277642d899df5c87a3966a349a798f224": 10 ** 12,
    "0x45dda9cb7c25131df268515131f647d726f50608": 10 ** 12,
    "0xeef1a9507b3d505f0062f2be9453981255b503c8": 10 ** 12,
    "0xa374094527e1673a86de625aa59517c5de346d32": 10 ** 12,
    "0x94ab9e4553ffb839431e37cc79ba8905f45bfbea": 10 ** 12,
}

# inverse 1 / price = 1/271149532.10105515=3.6880019384555252e-09
INVERSE_POOL_PRICE = {
    "0xc31e54c7a869b9fcbecc14363cf510d1c41fa443": False,
    "0xc24f7d8e51a64dc1238880bd00bb961d54cbeb29": False,
    "0x1aeedd3727a6431b8f070c0afaa81cc74f273882": False, 
    "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8": True,
    "0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801": False,
    "0xa6cc3c2531fdaa6ae1a3ca84c2855806728693e8": False,
    "0x99ac8ca7087fa4a2a1fb6357269965a2014abc35": False,
    "0x1fb3cf6e48f1e7b10213e7b6d87d4c073c7fdb7b": True,
    "0xfad57d2039c21811c8f2b5d5b65308aa99d31559": False,
    "0xd0fc8ba7e267f2bc56044a7715a489d851dc6d78": False,
    "0xcda53b1f66614552f834ceef361a8d12a0b8dad8": False,
    "0xac70bd92f89e6739b3a08db9b6081a923912f73d": False,
    "0xa7bb0d95c6ba0ed0aca70c503b34bc7108589a47": False,
    "0x1c3140ab59d6caf9fa7459c6f83d4b52ba881d36": False,
    "0xd0b53d9277642d899df5c87a3966a349a798f224": False,
    "0x45dda9cb7c25131df268515131f647d726f50608": True,
    "0xeef1a9507b3d505f0062f2be9453981255b503c8": False,
    "0xa374094527e1673a86de625aa59517c5de346d32": False,
    "0x94ab9e4553ffb839431e37cc79ba8905f45bfbea": True
}
# map networks brownie(key) with networks frontend
MAPPING_NETWORKS_NAME = {
    "ethereum-mainnet" : "mainnet",
    "arbitrum-mainnet":  "arbitrum",
    "optimism-mainnet": "optimism",
    "linea-mainnet": "linea",
    "zksync-mainnet": "zksync",
    "scrollrpcio": "scroll",
    "base-mainnet": "base",
    "polygon-mainnet": "polygon",
}

# Initialize a session using Amazon DynamoDB
dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('yourtablenameevent')

def get_pool_subscriptions_per_network(current_network):
    if current_network == "ethereum-mainnet":
        return {
            "uniswap":[config["networks"][network.show_active()]["uni_pool_address_eth_usdc"],
            config["networks"][network.show_active()]["uni_pool_address_eth_uni"],
            config["networks"][network.show_active()]["uni_pool_address_eth_link"],
            config["networks"][network.show_active()]["uni_pool_address_usdc_btc"],
            config["networks"][network.show_active()]["uni_pool_address_usdc_link"],
            config["networks"][network.show_active()]["uni_pool_address_usdc_uni"],
        ]}
    elif current_network == "arbitrum-mainnet":
        return {
            "uniswap": [config["networks"][network.show_active()]["uni_pool_address_eth_usdc"],
            config["networks"][network.show_active()]["uni_pool_address_eth_uni"],
            config["networks"][network.show_active()]["uni_pool_address_eth_gmx"],
            config["networks"][network.show_active()]["uni_pool_address_usdc_arb"],
            config["networks"][network.show_active()]["uni_pool_address_usdc_btc"],
            config["networks"][network.show_active()]["uni_pool_address_usdc_gmx"],
            ],
            
        }
    elif current_network == "optimism-mainnet":
        return {
            "uniswap": [config["networks"][network.show_active()]["uni_pool_address_eth_usdc"]],
            "uniswap": [config["networks"][network.show_active()]["uni_pool_address_usdc_op"]],
            "uniswap": [config["networks"][network.show_active()]["uni_pool_address_usdc_btc"]],
        }
    elif current_network == "base-mainnet":
        return {
            "uniswap": [config["networks"][network.show_active()]["uni_pool_address_eth_usdc"]],
        }
    elif current_network == "polygon-mainnet":
        return {
            "uniswap": [config["networks"][network.show_active()]["uni_pool_address_eth_usdc"]],
            "uniswap": [config["networks"][network.show_active()]["uni_pool_address_usdc_btc"]],
            "uniswap": [config["networks"][network.show_active()]["uni_pool_address_usdc_matic"]],
            "uniswap": [config["networks"][network.show_active()]["uni_pool_address_usdc_link"]],
        }
    raise Exception("Network not supported")

def listen_event_exchange(exchange):
    if exchange == "uniswap":
        return config["networks"][network.show_active()]["uni_swap_event"]
    
def sqrt_to_price(sqrtPriceX96):
    return sqrtPriceX96 ** 2 / 2**192

def get_sqrtPriceX96_int(sqrtPriceX96_hex):
    sqrtPriceX96 = int(str(sqrtPriceX96_hex),16)
    return sqrtPriceX96

def decrypt_event_swap(event_transaction):
    amount0, amount1, sqrtPriceX96, liquidity, tick = [event_transaction['data'][2:][i:i+64] for i in range(0, len(event_transaction['data'][2:]), 64)]
    return amount0, amount1, sqrtPriceX96, liquidity, tick 

def decrypt_pool(pool_address):
    """
    Add more information about the pool if needed
    """
    tokens_address = POOL_TOKENS_ADDRESS[pool_address]
    token0_ticker, token1_ticker = get_ticker(tokens_address[0], tokens_address[1])
    return token0_ticker, token1_ticker

def get_ticker(token0_adress, token1_address):
    dict_address_token = MAPPING_ADRESS_TICKER[network.show_active()]
    token0_ticker = dict_address_token[token0_adress]
    token1_ticker = dict_address_token[token1_address]
    return token0_ticker, token1_ticker

def subscription():
    subscribe_requests = []
    protocols_pools = get_pool_subscriptions_per_network(network.show_active())
    for exchange, contract_addresses in protocols_pools.items():
        event_exchange = listen_event_exchange(exchange)
        for address in contract_addresses:
            subscribe_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_subscribe",
                "params": ["logs", {"address": address,
                            "topics": [event_exchange]}]
            }
            subscribe_requests.append(subscribe_request)
    return subscribe_requests

def format_swap_event(event, protocols_pools):
    """
    Structure format example: 
    {
        "ticker#network": f"{ticker}#network", 
        "exchange": "uniswap",
        "price": price,
        "is_eth": False, 
        "timestamp": int(time.time())
    }
    """
    ticker = event[0]
    price = f"{round(float(event[1]), 2):.2f}" if float(event[1]) > 1 else f"{round(float(event[1]), 8):.8f}"
    _network = MAPPING_NETWORKS_NAME[network.show_active()]
    send_message = {
        "ticker#network": f"{ticker.upper()}#{_network.upper()}", 
        "exchange": protocols_pools.lower(), 
        "price": price, 
        "timestamp": int(time.time()), 
        "is_eth": event[3]
    }
    return send_message

def format_message_websocket_sever(event, type_event):
    protocols_pools = MAPPING_POOL_PROTOCOLE[event[2]]
    if type_event =="swap_event":
        message = format_swap_event(event, protocols_pools)
        return message
    raise Exception("Only support sending swap event message for the moment")

def send_subscribe_request(websocket, subscribe_requests):
    tasks = []
    for subscribe_request in subscribe_requests:
        tasks.append(websocket.send(json.dumps(subscribe_request)))
    return tasks

def apply_decimal_pool(pool_address, amount):
    amount = amount * POOL_DECIMAL_PRICE[pool_address]
    return amount

def devise_pricing_event(token0_ticker, token1_ticker):
    """
    If one of the tokens is USDC, return the other token and indicate that it is not priced in ETH.
    If neither token is USDC, return the token that is not ETH and indicate that it is priced in ETH.
    """
    if "USDC" in [token0_ticker, token1_ticker]:
        if token0_ticker=="USDC":
            return token1_ticker, False
        if token1_ticker=="USDC":
            return token0_ticker, False
    else:
        if token0_ticker=="ETH":
            return token1_ticker, True
        if token1_ticker=="ETH":
            return token0_ticker, True

def handle_event(event):
    event = json.loads(event)
    type_event = EVENT_TYPE[event['params']['result']['topics'][0]]
    if type_event == "swap_event":
        pool_address = event['params']['result']['address']
        amount0, amount1, sqrtPriceX96, liquidity, tick = decrypt_event_swap(event['params']['result'])
        token0_ticker, token1_ticker = decrypt_pool(pool_address)
        sqrtPriceX96 = get_sqrtPriceX96_int(str(sqrtPriceX96))
        price = sqrt_to_price(sqrtPriceX96)
        _inverse_pool_price = INVERSE_POOL_PRICE[pool_address]
        if _inverse_pool_price==True:
            price = 1/price
        ticker, is_devise_eth = devise_pricing_event(token0_ticker, token1_ticker)
        if is_devise_eth == False:
            price = apply_decimal_pool(pool_address, price)
        return (ticker, price, pool_address, is_devise_eth), type_event
    raise Exception("We do not support other pool event")

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
                    _subscription = subscription()
                    tasks = send_subscribe_request(receive_ws, _subscription)
                    await asyncio.gather(*tasks)
                    while True:
                        # Receive data from the first WebSocket server
                        event = await receive_ws.recv()
                        # avoid first message subscription event
                        if "subscription" in event:
                            event, type_event = handle_event(event)
                            format_message = format_message_websocket_sever(event, type_event)
                            # Send the received data to the second WebSocket server
                            await send_ws.send(json.dumps({'action': 'SendMessage', 'message': json.dumps(format_message)}))
                            await send_message_to_dynamodb(format_message)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(10)

async def run(receive_uri, send_uri):
    tasks = [receive_and_send_data(uri, send_uri) for uri in receive_uri]
    await asyncio.gather(*tasks)

def main():
    _receive_uris = receive_uris[network.show_active()]
    asyncio.run(run(_receive_uris, send_uri))

if __name__ == "__main__":
    main()