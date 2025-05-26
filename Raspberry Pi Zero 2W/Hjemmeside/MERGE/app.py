from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_socketio import SocketIO, emit
import sqlite3
import threading
import DB
import graphs
from time import sleep
from datetime import datetime

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

# Always push the last 5 min graph
def update_graphs():
    graph_img = graphs.create_graph(9, minuts=5)  # Temperature (AHT)
    if graph_img:
        socketio.emit('temp_graph', {'image': graph_img})
    graph_img = graphs.create_graph(3, 4, minuts=5)  # TVOC & eCO2
    if graph_img:
        socketio.emit('CO2TVOCgraph', {'image': graph_img})
    graph_img = graphs.create_graph(4, minuts=5)  # eCO2
    if graph_img:
        socketio.emit('air_graph', {'image': graph_img})

# Update the emit loop to simply call update_graphs using the current_minutes value.
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
            'temperature': row[8],  # Temp_aht
            'humidity': row[9],     # Rh_aht
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

@app.route('/om')
def om():
    return render_template('om.html')

@app.route('/indstillinger')
def indstillinger():
    return render_template('indstillinger.html')

@app.route('/send', methods=['POST'])
def receive_data():
    data = request.get_json()
    print("Received from ESP32:", data)
    if 'ID' in data:
        print(f"New Temp reading received from ESP-{data['ID']}")
        DB.create_new_temp_reading(
            data['Aqi'], data['Tvoc'], data['Eco2'], data['Rh_ens'],
            data['Eco2_rating'], data['Tvoc_rating'], data['Temp_ens'],
            data['Temp_aht'], data['Rh_aht'], esp_id=data['ID']
        )
        conn = sqlite3.connect('sensordata.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT esp_id, Tempaht, Rhaht, timestamp
            FROM environment
            WHERE timestamp = (SELECT MAX(timestamp) FROM environment WHERE esp_id = environment.esp_id)
        ''')
        sensor_data = cursor.fetchall()
        conn.close()
        sensors = {}
        current_time = datetime.now()
        for row in sensor_data:
            esp_id = f'esp32_{row[0]}'
            timestamp = datetime.fromisoformat(row[3].replace(' ', 'T'))
            status = 'online' if (current_time - timestamp).total_seconds() < 60 else 'offline'
            sensors[esp_id] = {
                'name': f'ESP32-{row[0]}',
                'temperature': row[1],
                'humidity': row[2],
                'status': status
            }
        socketio.emit('sensor_update', sensors)
    response = {"message": f"Hello ESP32, got your value: {data}"}
    return jsonify(response)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['psw']
        conn = sqlite3.connect('username.db')
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            session['role'] = user[0]
            if user[0] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('vis_brugere'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET'])
def admin():
    conn = sqlite3.connect('username.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    brugere = cursor.fetchall()
    conn.close()
    return render_template('admin.html', brugere=brugere)

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    conn = sqlite3.connect('username.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    conn = sqlite3.connect('username.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ?, password = ?, role = ? WHERE id = ?", (username, password, role, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    conn = sqlite3.connect('username.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/brugere')
def vis_brugere():
    conn = sqlite3.connect('username.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role FROM users")
    brugere = cursor.fetchall()
    conn.close()
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    conn2 = sqlite3.connect('sensordata.db')
    cursor2 = conn2.cursor()
    cursor2.execute('''
        SELECT DATE(starttimestamp) AS dato, SUM(paid) AS salary
        FROM sessions
        WHERE name = ?
        GROUP BY DATE(starttimestamp)
        ORDER BY dato DESC
        LIMIT 50
    ''', (username,))
    data = cursor2.fetchall()
    conn2.close()
    return render_template('brugere.html', brugere=brugere, data=data)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    tagid = request.form['tagid']
    salary = float(request.form['salary'])
    otlimit = float(request.form['otlimit'])
    otform = float(request.form['otform'])
    DB.create_new_employee(name, tagid, salary, otlimit, otform)
    return redirect(url_for('admin'))

@app.route('/session_update/<name>', methods=['POST'])
def session_update(name):
    DB.sessionupdate(name)
    return redirect(url_for('admin'))

@socketio.on('connect')
def handle_connect():
    print('Client connected')
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
    emit('sensor_update', sensors)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    init_username_db()
    DB.init_db()
    threading.Thread(target=emit_loop, daemon=True).start()
    socketio.run(app, host='0.0.0.0', debug=True)