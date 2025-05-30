import DB # All DB-related things go here!
import graphs # Graph stuff goes here
import threading # For socketIO emit graph function
import base64 # Graphs and graphics
import sqlite3 # DB for login-system
import os
from datetime import datetime, timedelta


from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_socketio import SocketIO # Websockets

from io import BytesIO # Graphs and stuff

from time import sleep

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MammutGed'
socketio = SocketIO(app)

# Webpage / Homepage route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/om')
def om():
    return render_template('om.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/indstillinger')
def indstillinger():
    return render_template('indstillinger.html')

@app.route('/kontakt')
def kontakt():
    return render_template('oldindex.html')

# Emit loop, that updates the graphs once every second (If the Raspberry Pi can even mangage that...)
def update_graphs():
    # Temp Graph
    graph_img = graphs.create_graph(9,10, 90) #See graph.datanames for explanation
    if graph_img:
        socketio.emit('temp_graph', {'image': graph_img})
    # Air Graph
    graph_img = graphs.create_graph(3,4, 90) #See graph.datanames for explanation
    if graph_img:
        socketio.emit('CO2TVOCgraph', {'image': graph_img}) 
    # LDR Graph
    graph_img = graphs.create_graph(11, 0, 90) #See graph.datanames for explanation
    if graph_img:
        socketio.emit('LDRgraph', {'image': graph_img}) 
def emit_loop():
    while True: 
        update_graphs()
        sleep(1)


@app.route('/send', methods=['POST'])
def receive_data():
    data = request.get_json()
    print("---------- New /send Request ----------")
    print(f"This is of datatype: {type(data)} .Raw data that was sent:")
    # Check to see if UID match anyone in the DB
    print(data)
    
    if data['ERRORS'] != 0:
        ''' machine, errortype, erroramount, errormessage '''
        error_type = "Unknown"
        if data['ID'] == 0 or data['ID'] == 1 or data['ID'] == 2:
            error_type = "Perhaps issues with sending a message"
        DB.report_error(data['ID'],error_type, data['ERRORS'], "Make sure WiFi connection is strong")
    if data['ID'] == 0: # ID = 0, New UID tag recived. Managening employee sessions
        response = DB.sessionupdate(DB.convert_uid_to_name(data['UID']))
        print("New UID reading recived from ESP-0")
        response["ID"] = 0
        response["Retry"] = 0
    elif data['ID'] == 1: # ID = 1, New Temp Reading
        print("New Temp reading recived from ESP-1")
        DB.create_new_temp_reading(data['Aqi'], data['Tvoc'], data['Eco2'], data['Rh_ens'], data['Eco2_rating'], data['Tvoc_rating'], data['Temp_ens'], data['Temp_aht'], data['Rh_aht'], data['LDR'])
        response = "Hello ESP 1"
    elif data['ID'] == 2: # ID = 1, New Temp Reading
        print("New Ventilation Call from ESP-2")
        aqi = DB.fetch_latest_AQI()
        if aqi <= 2:
            motor_on = 0
        else:
            motor_on = 1
        response = {
            'ID' : 2,
            'Retry' : 0,
            'motor_on' : motor_on
        }
    else:
        response = {"message": "Hello ESP32, got your value, but did not do anything with it: " + str(data)}
    print(f"This is the data that was returned to ESP32: {response}")
    print("---------- End of /send Request ----------")
    return jsonify(response)

# Login system

def init_db():
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

    # Indsæt admin og brugere hvis de ikke allerede findes
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', '1234', 'admin')")
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('Bo', '1234', 'bruger')")
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('Anders', '1234', 'bruger')")

    conn.commit()
    conn.close()

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
            role = user[0]
            session['username'] = username  # Gem brugerens navn i session
            session['role'] = role          # Gem rollen også
            if role == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('vis_brugere'))
        else:
            return redirect(url_for('index'))

    return render_template('index.html')

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
    # Hent brugere fra users-tabellen
    conn1 = sqlite3.connect('username.db')
    cursor1 = conn1.cursor()
    cursor1.execute("SELECT id, username, password, role FROM users")
    brugere = cursor1.fetchall()
    conn1.close()


    username = session.get('username')

    conn2 = sqlite3.connect('example.db')
    cursor2 = conn2.cursor()

    # Hent løndata for de sidste 60 dage
    # vise bruger er i example og username

    cursor2.execute('''
        SELECT DATE(starttimestamp) AS dato, paid AS salary
        FROM sessions
        WHERE name = ? AND DATE(starttimestamp) >= DATE('now', '-60 days')
        ORDER BY dato DESC
    ''', (username,))
    salary_data = cursor2.fetchall()

    cursor2.execute('SELECT * FROM sessions WHERE name = ?', (username,))
    person_data = cursor2.fetchall()

    # Beregn status ud fra seneste starttimestamp
    if person_data:
        try:
            last_timestamp_str = person_data[-1][2]
            last_timestamp = datetime.fromisoformat(last_timestamp_str)

            if datetime.now() - last_timestamp < timedelta(hours=5):
                status = "på arbejdet"
            else:
                status = "har fri"
        except Exception as e:
            status = f"Fejl i tidsformat: {e}"
    else:
        status = "Ingen data"

    conn2.close()

    return render_template(
        'brugere.html',
        brugere=brugere,
        salary_data=salary_data,
        person_data=person_data,
        status=status
    )

# login system slut ^^^^

if __name__ == '__main__': # Checks to see if this file is run as the main file
    threading.Thread(target=emit_loop, daemon=True).start() #Starts Sensor Loop with threading enabled
    init_db() # Opstarter login DB
    socketio.run(app, host='0.0.0.0', port=5000) # Hoster på port 5000
