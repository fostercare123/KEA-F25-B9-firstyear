import eventlet
eventlet.monkey_patch()  # <-- Required for Flask-SocketIO to work correctly

from flask import Flask, render_template
from flask_socketio import SocketIO
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return render_template('index.html')

def sensor_thread():
    while True:
        data = {
            'temperature': random.randint(20, 30),
            'humidity': random.randint(30, 60)
        }
        print('Emitting:', data)
        socketio.emit('sensor_update', data)
        socketio.sleep(2)  # Important: use socketio.sleep, NOT time.sleep!

@socketio.on('connect')
def handle_connect():
    print("Client connected!")

if __name__ == "__main__":
    socketio.start_background_task(sensor_thread)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
