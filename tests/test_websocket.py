import asyncio
import websockets
import json
import time
import pytest
import allure


BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"
MAX_LATENCY = 1.0


@pytest.fixture()
async def ws_connection():
    try:
        async with websockets.connect(BINANCE_WS_URL) as websocket:
            print("Connected to Binance websocket")
            yield websocket
    except Exception as e:
        print(f"Unexpected error while testing WebSocket {e}")
    except websockets.exceptions.ConnectionClosed:
        print(f"Error: WebSocket connection was closed.")


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_binance_websocket(ws_connection):
    received_prices = []
    latencies = []
    for _ in range(10):
        start_time = time.time()
        message = await ws_connection.recv()
        end_time = time.time()
        latency = end_time - start_time
        latencies.append(latency)
        data = json.loads(message)
        assert "p" in data, "Error: missing field 'p' (price)"
        assert "s" in data, "Error: missing field 's' (symbol)"
        assert "q" in data, "Error: missing field 'q' (quantity)"
        price = float(data["p"])
        symbol = data["s"]
        quantity = float(data["q"])
        print(
            f"Trade received: {symbol}, Price: {price} USDT, Quantity: {quantity}, Latency: {latency:.3f} s")
        received_prices.append(price)
        assert price > 0, "Error: invalid price received."
        assert latency < MAX_LATENCY, f"Warning: Latency {float(latency)} exceeds {MAX_LATENCY:.3f}"
    assert received_prices, "Error: No BTC/USDT priced received"
    avg_latency = float(sum(latencies) / len(latencies))
    print(f"Avg WebSocket Latency: {avg_latency:.3f} s")
    print("WebSocket test completed successfully")
