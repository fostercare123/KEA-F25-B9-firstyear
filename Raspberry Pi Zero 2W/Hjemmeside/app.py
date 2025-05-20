from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

# Sample data for demonstration (you'll replace this with ESP32 data later)
sample_sensors = {
    'esp32_1': {
        'name': 'Living Room',
        'temperature': 22.5,
        'humidity': 45,
        'status': 'online'
    },
    'esp32_2': {
        'name': 'Bedroom',
        'temperature': 21.0,
        'humidity': 50,
        'status': 'online'
    },
    'esp32_3': {
        'name': 'Kitchen',
        'temperature': 23.5,
        'humidity': 55,
        'status': 'online'
    }
}

@app.route('/')
def index():
    return render_template('index.html', sensors=sample_sensors)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', sensors=sample_sensors)

@app.route('/om')
def om():
    return render_template('om.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('sensor_update', sample_sensors)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)