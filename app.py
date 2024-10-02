from flask import Flask, render_template, jsonify, request
import requests
from flask_cors import CORS
import logging
import asyncio
import plotly.graph_objects as go
import websockets
import json

app = Flask(__name__)
CORS(app)  # Дозволяємо CORS для всіх доменів та методів

# Налаштування журналювання
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

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

async def start_websocket_connection():
    if not getattr(start_websocket_connection, "started", False):
        await connect()
        start_websocket_connection.started = True

def start_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_websocket_connection())
    loop.run_forever()

@app.route('/get-config', methods=['POST'])
def get_config():
    url = "http://localhost:4000/config"
    response = requests.put(url, headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        response_data = response.json()
        config_data = response_data.get('config', {})
        return jsonify({
            "measurementsPerRotation": config_data.get('measurementsPerRotation', 0),
            "rotationSpeed": config_data.get('rotationSpeed', 0),
            "targetSpeed": config_data.get('targetSpeed', 0)
        })
    else:
        return jsonify({
            "status_code": response.status_code,
            "error": "Не вдалося отримати дані"
        })

@app.route('/')
def index():
    response = requests.post('http://localhost:5000/get-config')

    if response.status_code == 200:
        json_data = response.json()  # Перетворюємо відповідь в JSON
    else:
        json_data = {"error": "Не вдалося отримати конфігурацію"}

    return render_template('index.html', json_data=json_data)

@app.route('/graph-data')
def graph_data():
    data = asyncio.run(get_data())
    if data:
        distance = data.get('distance', 0)
        scanAngle = data.get('scanAngle', 0)
        power = data.get('echoResponses', [{}])[0].get('power', 0)

        if power >= 1000:
            power = 1000
        
        marker_color = 'green' if power < 0.05 else 'blue'
        marker_size = 10 + power / 10  # Розмір точки
        marker_symbol = 'circle' if power < 0.05 else 'square'  # Форма точки

        hover_text = f"Distance: {distance}<br>Angle: {scanAngle}<br>Power: {power}"

        fig = go.Figure(data=go.Scatterpolar(
            r=[distance],
            theta=[scanAngle],
            mode='markers',
            marker=dict(
                color=marker_color,  # Колір точки
                size=marker_size,  # Розмір точки
                symbol=marker_symbol  # Форма точки
            ),
            hovertext=hover_text,  # Текст при наведенні
            hoverinfo="text"  # Показуємо лише текст
        ))

        fig.update_layout(showlegend=False, polar=dict(radialaxis=dict(range=[0, 200])))
        graphJSON = fig.to_json()
        return jsonify(graphJSON)
    else:
        return jsonify({"error": "Немає даних"})

@app.route('/send-config', methods=['POST'])
def send_config():
    data = request.json
    url = "http://localhost:4000/config"
    response = requests.put(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
    if response.status_code == 200:
        asyncio.run(send_config_to_websocket(data))  # Відправляємо конфігурацію через WebSocket
        return jsonify({
            "status_code": response.status_code,
            "response": "Конфігурація оновлена",
            "updated_config": data
        })
    else:
        return jsonify({
            "status_code": response.status_code,
            "error": "Помилка відправки конфігурації"
        })

if __name__ == "__main__":
    import threading
    event_loop_thread = threading.Thread(target=start_event_loop)
    event_loop_thread.start()

    app.run(debug=True, use_reloader=False)  # Вимкнуто use_reloader, щоб не створювати додаткові потоки
