import sqlite3
from datetime import datetime, timezone

def init_db():
    try:
        conn = sqlite3.connect("sensordata.db", check_same_thread=False)
        cursor = conn.cursor()

        # Drop existing environment table to ensure correct schema
        cursor.execute("DROP TABLE IF EXISTS environment")
        
        # Create main table
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
        
        # Create sessions table
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
        
        # Create environment table with esp_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS environment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                esp_id INTEGER NOT NULL,
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

        # Insert sample data with esp_id (REMOVED to avoid polluting environment table)
        # cursor.execute('''
        #     INSERT OR IGNORE INTO environment (
        #         esp_id, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht, timestamp
        #     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        # ''', (1, 1, 56, 469, 0.1953125, 'Excellent - Target level', 'Good', 276.0063, 26.16, 40.26, '2025-05-22 09:42:45'))

        # cursor.execute('''
        #     INSERT OR IGNORE INTO environment (
        #         esp_id, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht, timestamp
        #     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        # ''', (2, 1.2, 60, 480, 0.2, 'Excellent', 'Good', 275.0, 25.8, 41.0, '2025-05-22 09:42:46'))

        # Insert sample data for sessions and main
        cursor.execute('''
            INSERT OR IGNORE INTO sessions (name, starttimestamp, salary, othours, otform)
            VALUES (?, ?, ?, ?, ?)
        ''', ('bruger1', '2025-05-01 10:00:00', 100.0, 6.0, 50.0))

        cursor.execute('''
            INSERT OR IGNORE INTO main (name, tagid, salary, otlimit, otform)
            VALUES (?, ?, ?, ?, ?)
        ''', ('bruger1', '0x1234', 100.0, 6.0, 50.0))

        conn.commit()
        print("Database initialized successfully with environment table including esp_id")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def fetch_all_temperatures():
    try:
        conn = sqlite3.connect("sensordata.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT esp_id, timestamp, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht FROM environment")
        data = cursor.fetchall()
        return data
    except sqlite3.Error as e:
        print(f"Error fetching temperatures: {e}")
        return []
    finally:
        conn.close()

def fetch_temps_last_x_minutes(minutes):
    try:
        conn = sqlite3.connect("sensordata.db", check_same_thread=False)
        cursor = conn.cursor()
        query = '''
            SELECT esp_id, timestamp, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht 
            FROM environment
            WHERE timestamp >= DATETIME('now', ?, 'utc')
        '''
        cursor.execute(query, (f'-{minutes} minutes',))
        data = cursor.fetchall()
        return data
    except sqlite3.Error:
        return []
    finally:
        conn.close()

def create_new_temp_reading(Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht, esp_id=1):
    try:
        conn = sqlite3.connect("sensordata.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO environment (esp_id, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (esp_id, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht))
        conn.commit()
    except sqlite3.Error:
        pass
    finally:
        conn.close()

def create_new_employee(name, tagid, salary, otlimit, otform):
    try:
        conn = sqlite3.connect("sensordata.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO main (name, tagid, salary, otlimit, otform)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, tagid, salary, otlimit, otform))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating employee: {e}")
    finally:
        conn.close()

def fetch_employees():
    try:
        conn = sqlite3.connect("sensordata.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM main")
        cluttered_names = cursor.fetchall()
        for i in range(len(cluttered_names)):
            print(f"Employee nr. {i} : {cluttered_names[i][0]}")
        return [name[0] for name in cluttered_names]
    except sqlite3.Error as e:
        print(f"Error fetching employees: {e}")
        return []
    finally:
        conn.close()

def check_employee_session(name):
    try:
        conn = sqlite3.connect("sensordata.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM sessions
            WHERE name = ? AND endtimestamp IS NULL
            LIMIT 1
        ''', (name,))
        data = cursor.fetchall()
        return data
    except sqlite3.Error as e:
        print(f"Error checking employee session: {e}")
        return []
    finally:
        conn.close()

def convert_uid_to_name(uid):
    try:
        conn = sqlite3.connect("sensordata.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM main WHERE tagid = ?", (uid,))
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Error converting UID to name: {e}")
        return None
    finally:
        conn.close()

def sessionupdate(name):
    try:
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
    except sqlite3.Error as e:
        print(f"Error updating session: {e}")
    finally:
        conn.close()

def fetch_latest_data():
    try:
        conn = sqlite3.connect("sensordata.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT esp_id, timestamp, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht
            FROM environment
            WHERE timestamp = (SELECT MAX(timestamp) FROM environment WHERE esp_id = environment.esp_id)
        ''')
        data = cursor.fetchall()
        return data
    except sqlite3.Error as e:
        print(f"Error fetching latest data: {e}")
        return []
    finally:
        conn.close()