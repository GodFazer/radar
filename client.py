import asyncio
import websockets
import json

# Змінна для зберігання кешованих даних
cached_data = None

async def send_config_to_websocket(config_data):
    uri = "ws://localhost:4000"  # Змініть на адресу вашого WebSocket сервера
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(config_data))  # Перетворюємо дані у JSON
        response = await websocket.recv()
        return response

async def connect():
    global cached_data
    uri = "ws://localhost:4000"
    try:
        async with websockets.connect(uri) as websocket:
            print("Підключено до WebSocket сервера")
            # Обробляємо повідомлення від сервера
            async for message in websocket:
                data = json.loads(message)
                if 'echoResponses' in data and data['echoResponses']:
                    data['distance'] = round(300_000 * data['echoResponses'][0]['time'] / 2, 2)
                    cached_data = data  # Зберігаємо дані в кеш
    except websockets.exceptions.ConnectionClosed as e:
        print(f"З'єднання закрито: {e.reason}")
    except Exception as e:
        print(f"Помилка WebSocket: {e}")

async def get_data():
    global cached_data
    return cached_data  # Повертаємо кешовані дані
