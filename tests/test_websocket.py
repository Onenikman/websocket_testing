import json
import time
import pytest
import os


BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"
MAX_LATENCY = 1.0


@pytest.mark.skipif(
    # GitHub sets this to "true" in CI
    os.environ.get("GITHUB_ACTIONS") == "true",
    reason="Skipped on GitHub Actions due to Binance WS restrictions"
)
@pytest.mark.parametrize("ws_connection", [BINANCE_WS_URL], indirect=True)
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


@pytest.mark.parametrize("user_response", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], indirect=True)
@pytest.mark.api_async
@pytest.mark.asyncio
async def test_user_data(user_response):
    assert user_response.status_code == 200
    data = user_response.json()
    assert "username" in data


@pytest.mark.parametrize("post_number", [(1), (2), (3), (4), (5), (6), (7), (8), (9), (10)])
@pytest.mark.api_async
@pytest.mark.asyncio
async def test_get_post(async_client, post_number):
    response = await async_client.get(f"/posts/{post_number}")
    assert response.status_code == 200
    assert response.json()["id"] == post_number


@pytest.mark.api_async
@pytest.mark.asyncio
async def test_get_post_by_id(get_post_by_id):
    assert get_post_by_id.status_code == 200
    json_data = get_post_by_id.json()
    assert "title" in json_data
    assert "body" in json_data
