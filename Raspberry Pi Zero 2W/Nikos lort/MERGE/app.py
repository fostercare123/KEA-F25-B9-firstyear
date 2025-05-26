from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_socketio import SocketIO, emit
import sqlite3
import threading
import DB
import graphs
from time import sleep
from datetime import datetime
import simulate_data

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

def init_username_db():
    conn = sqlite3.connect('username.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', '1234', 'admin')")
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('bruger1', 'abcd', 'bruger')")
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('bruger2', 'abcd', 'bruger')")
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin2', 'abcd', 'admin')")
    conn.commit()
    conn.close()

current_minutes = 5

def update_graphs():
    global current_minutes
    graph_img = graphs.create_graph(9, minuts=current_minutes)  # Temperature (AHT)
    if graph_img:
        socketio.emit('temp_graph', {'image': graph_img, 'minutes': current_minutes})

    graph_img = graphs.create_graph(3, 4, minuts=current_minutes)  # TVOC & eCO2
    if graph_img:
        socketio.emit('CO2TVOCgraph', {'image': graph_img, 'minutes': current_minutes})

    graph_img = graphs.create_graph(4, minuts=current_minutes)  # eCO2
    if graph_img:
        socketio.emit('air_graph', {'image': graph_img, 'minutes': current_minutes})

def emit_loop():
    while True:
        update_graphs()
        sleep(4)

@app.route('/')
def index():
    conn = sqlite3.connect('sensordata.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT esp_id, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht, timestamp
        FROM environment
        WHERE timestamp = (SELECT MAX(timestamp) FROM environment WHERE esp_id = environment.esp_id)
    ''')
    data = cursor.fetchall()
    conn.close()
    sensors = {}
    current_time = datetime.now()
    for row in data:
        esp_id = f'esp32_{row[0]}'
        timestamp = datetime.fromisoformat(row[10].replace(' ', 'T'))
        status = 'online' if (current_time - timestamp).total_seconds() < 60 else 'offline'
        sensors[esp_id] = {
            'name': f'ESP32-{row[0]}',
            'temperature': row[8],
            'humidity': row[9],
            'status': status
        }
    return render_template('index.html', sensors=sensors)

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('sensordata.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT esp_id, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht, timestamp
        FROM environment
        WHERE timestamp = (SELECT MAX(timestamp) FROM environment WHERE esp_id = environment.esp_id)
    ''')
    data = cursor.fetchall()
    cursor.execute('''
        SELECT COUNT(*) 
        FROM environment 
        WHERE DATE(timestamp) = DATE('now')
    ''')
    data_points = cursor.fetchone()[0]
    conn.close()
    sensors = {}
    current_time = datetime.now()
    for row in data:
        esp_id = f'esp32_{row[0]}'
        timestamp = datetime.fromisoformat(row[10].replace(' ', 'T'))
        status = 'online' if (current_time - timestamp).total_seconds() < 60 else 'offline'
        sensors[esp_id] = {
            'name': f'ESP32-{row[0]}',
            'temperature': row[8],
            'humidity': row[9],
            'status': status
        }
    return render_template('dashboard.html', sensors=sensors, data_points=data_points)

@app.route('/send', methods=['POST'])
def receive_data():
    data = request.get_json()
    if 'ID' in data:
        DB.create_new_temp_reading(
            data['Aqi'], data['Tvoc'], data['Eco2'], data['Rh_ens'],
            data['Eco2_rating'], data['Tvoc_rating'], data['Temp_ens'],
            data['Temp_aht'], data['Rh_aht'], esp_id=data['ID']
        )
        sensors = {}
        for row in DB.fetch_latest_data():
            esp_id = f'esp32_{row[0]}'
            sensors[esp_id] = {
                'name': f'ESP32-{row[0]}',
                'temperature': row[8],
                'humidity': row[9],
                'status': 'online'
            }
        socketio.emit('sensor_update', sensors)
    return jsonify({"message": "Data received successfully"})

@socketio.on('connect')
def handle_connect():
    sensors = {}
    for row in DB.fetch_latest_data():
        esp_id = f'esp32_{row[0]}'
        sensors[esp_id] = {
            'name': f'ESP32-{row[0]}',
            'temperature': row[8],
            'humidity': row[9],
            'status': 'online'
        }
    emit('sensor_update', sensors)

@socketio.on('request_historical')
def handle_historical(minutes):
    global current_minutes
    try:
        current_minutes = int(minutes)
    except ValueError:
        current_minutes = 5
    update_graphs()

@app.route('/om')
def om():
    return render_template('om.html')

@app.route('/indstillinger')
def indstillinger():
    return render_template('indstillinger.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('psw')
        conn = sqlite3.connect('username.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/brugere')
def vis_brugere():
    data = [
        ('2025-05-01', 1000),
        ('2025-05-02', 1200),
        ('2025-05-03', 1100),
    ]
    return render_template('brugere.html', data=data)

@app.route('/betalinger')
def betalinger():
    salary_data = [
        ('2025-05-01', 5000),
        ('2025-05-02', 6000),
        ('2025-05-03', 5500),
    ]
    return render_template('betalinger.html', salary_data=salary_data)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect('username.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
    cursor.execute("SELECT * FROM users")
    brugere = cursor.fetchall()
    conn.close()
    return render_template('admin.html', brugere=brugere)

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    conn = sqlite3.connect('username.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    conn = sqlite3.connect('username.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ?, password = ?, role = ? WHERE id = ?", (username, password, role, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    simulation_thread = threading.Thread(target=simulate_data.start_simulation, daemon=True)
    simulation_thread.start()

    init_username_db()
    DB.init_db()
    threading.Thread(target=emit_loop, daemon=True).start()
    socketio.run(app, host='0.0.0.0', debug=False)