from flask_socketio import SocketIO, emit
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os




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

    conn = sqlite3.connect('usernamek.db')
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
    conn1 = sqlite3.connect('username.db')
    cursor1 = conn1.cursor()
    cursor1.execute("SELECT id, username, password, role FROM users")
    brugere = cursor1.fetchall()
    conn1.close()


    """
    username = session.get('username')

    conn2 = sqlite3.connect('example.db')
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
    """
    data = [('2025-05-01', 100), ('2025-05-02', 250)]


   
    return render_template('brugere.html', brugere=brugere, data=data)











if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)