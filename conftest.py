import websockets
import pytest
import httpx


@pytest.fixture(scope="function")
async def ws_connection(request):
    try:
        async with websockets.connect(request.param) as websocket:
            print("Connected to Binance websocket")
            yield websocket
    except Exception as e:
        print(f"Unexpected error while testing WebSocket {e}")
    except websockets.exceptions.ConnectionClosed:
        print(f"Error: WebSocket connection was closed.")
    except websockets.exceptions.InvalidStatusCode as e:
        print(
            f"Error: WebSocket connection was closed because of invalid status code: {e}.")


@pytest.fixture(scope="function")
async def user_response(request):
    user_id = request.param  # gets param from @pytest.mark.parametrize
    async with httpx.AsyncClient(base_url="https://jsonplaceholder.typicode.com") as client:
        response = await client.get(f"/users/{user_id}")
    return response


@pytest.fixture(scope="function")
async def async_client():
    async with httpx.AsyncClient(base_url="https://jsonplaceholder.typicode.com") as client:
        yield client


@pytest.fixture(scope="function", params=[(1), (2), (3), (4), (5)])
async def get_post_by_id(request):
    async with httpx.AsyncClient(base_url=f"https://jsonplaceholder.typicode.com") as client:
        response = await client.get(f"/posts/{request.param}")
        yield response
