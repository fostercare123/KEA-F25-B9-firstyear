from flask_socketio import SocketIO, emit
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from datetime import datetime, timedelta




### 
# Database men username data. 
# hedder username.db : id username passeword role
# 
# 
#  ####


### ### 




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



#### Logind system 


# Funktion til at sikre databasen og brugere er oprettet
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
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('bruger1', 'abcd', 'bruger')")
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('bruger2', 'abcd', 'bruger')")
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin2', 'abcd', 'admin')")

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
            session['username'] = username  # <- Gem brugerens navn i session
            session['role'] = role          # <- Gem rollen også
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





if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)