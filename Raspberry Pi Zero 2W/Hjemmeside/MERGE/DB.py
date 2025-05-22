import sqlite3
from datetime import datetime, timezone

# Initialize sensordata.db
def init_db():
    conn = sqlite3.connect("sensordata.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            tagid TEXT NOT NULL,
            salary REAL NOT NULL,
            otlimit REAL NOT NULL,
            otform REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            starttimestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            endtimestamp DATETIME,
            salary REAL NOT NULL,
            hours REAL,
            othours REAL NOT NULL,
            otform REAL NOT NULL,
            paid REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS environment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            Aqi REAL,
            Tvoc REAL,
            Eco2 REAL,
            Rhens REAL,
            Eco2rating TEXT,
            Tvocrating TEXT,
            Tempens REAL,
            Tempaht REAL,
            Rhaht REAL
        )
    ''')
    # Insert sample data for testing
    cursor.execute("INSERT OR IGNORE INTO environment (Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht) "
                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (1, 56, 469, 0.1953125, 'Excellent - Target level', 'Good', 276.0063, 26.16, 40.26))
    cursor.execute("INSERT OR IGNORE INTO sessions (name, starttimestamp, salary, othours, otform) "
                  "VALUES (?, ?, ?, ?, ?)", ('bruger1', '2025-05-01 10:00:00', 100.0, 6.0, 50.0))
    cursor.execute("INSERT OR IGNORE INTO main (name, tagid, salary, otlimit, otform) "
                  "VALUES (?, ?, ?, ?, ?)", ('bruger1', '0x1234', 100.0, 6.0, 50.0))
    conn.commit()
    conn.close()

# Fetch all sensor readings
def fetch_all_temperatures():
    conn = sqlite3.connect("sensordata.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM environment")
    data = cursor.fetchall()
    conn.close()
    return data

def fetch_temps_last_x_minutes(minutes):
    conn = sqlite3.connect("sensordata.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM environment
        WHERE timestamp >= DATETIME('now', ?)
    ''', (f'-{minutes} minutes',))
    data = cursor.fetchall()
    conn.close()
    return data

def create_new_temp_reading(Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht):
    conn = sqlite3.connect("sensordata.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO environment (Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht))
    conn.commit()
    conn.close()

def create_new_employee(name, tagid, salary, otlimit, otform):
    conn = sqlite3.connect("sensordata.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO main (name, tagid, salary, otlimit, otform)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, tagid, salary, otlimit, otform))
    conn.commit()
    conn.close()

def fetch_employees():
    conn = sqlite3.connect("sensordata.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM main")
    cluttered_names = cursor.fetchall()
    for i in range(len(cluttered_names)):
        print(f"Employee nr. {i} : {cluttered_names[i][0]}")
    conn.close()
    return [name[0] for name in cluttered_names]

def check_employee_session(name):
    conn = sqlite3.connect("sensordata.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM sessions
        WHERE name = ? AND endtimestamp IS NULL
        LIMIT 1
    ''', (name,))
    data = cursor.fetchall()
    conn.close()
    return data

def convert_uid_to_name(uid):
    conn = sqlite3.connect("sensordata.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM main WHERE tagid = ?", (uid,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def sessionupdate(name):
    conn = sqlite3.connect("sensordata.db", check_same_thread=False)
    cursor = conn.cursor()
    check = check_employee_session(name)
    if not check:
        print(f"Starting new session for employee {name}")
        cursor.execute('''
            SELECT * FROM main WHERE name = ?
        ''', (name,))
        info_from_main = cursor.fetchall()
        if not info_from_main:
            conn.close()
            return
        salary = info_from_main[0][3]
        othours = info_from_main[0][4]
        otform = info_from_main[0][5]
        cursor.execute('''
            INSERT INTO sessions (name, salary, othours, otform)
            VALUES (?, ?, ?, ?)
        ''', (name, salary, othours, otform))
        conn.commit()
    else:
        print(f"Ending session for {name}")
        cursor.execute('''
            SELECT id, starttimestamp, othours, otform, salary FROM sessions
            WHERE name = ? AND endtimestamp IS NULL
        ''', (name,))
        current_session = cursor.fetchall()
        if current_session:
            start = datetime.fromisoformat(current_session[0][1]).replace(tzinfo=timezone.utc)
            salary = current_session[0][4]
            otform = current_session[0][3]
            othours = current_session[0][2]
            end = datetime.now(timezone.utc)
            delta = end - start
            min_worked = int(delta.total_seconds() / 60 + 1)
            hours_worked = round(min_worked / 60, 2)
            otpaid = 0
            if hours_worked >= othours:
                otpaid = (hours_worked - othours) * otform
            paid = hours_worked * salary + otpaid
            cursor.execute('''
                UPDATE sessions 
                SET endtimestamp = ?, hours = ?, paid = ?
                WHERE name = ? AND endtimestamp IS NULL
            ''', (end, hours_worked, paid, name))
            conn.commit()
    conn.close()