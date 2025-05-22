import sqlite3
import time
from datetime import datetime, timezone


### Database
conn = sqlite3.connect("example.db", check_same_thread=False)
cursor = conn.cursor()

### MAIN


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


### SESSIONS
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

### environment
# Example
# {'ID': 1, 'Aqi': 2, 'Tvoc': 73, 'Eco2': 502, 'Rh_ens': 0.1953125,
#  'Eco2_rating': 'Excellent - Target level', 'Tvoc_rating': 'Good',
#  'Temp_ens': 276.0063, 'Temp_aht': 25.67, 'Rh_aht': 40.45, 'ERRORS': 0}
# 

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
conn.close() #THIS BIT LAST!!!
# Api Tvoc Eco2 Rhens Eco2rating Tvocrating Tempens Tempaht Rhaht
# Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht



# Function to fetch all readings
def fetch_all_temperatures():
    # Connect to the database
    # conn = sqlite3.connect("example.db")
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM main")
    return cursor.fetchall()
    conn.close()

def fetch_temps_last_x_minutes(minutes):
    # This ^ function returns a list of all types of readings the last x minuttes
    # Connect to the database
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()

    # Query to get temperatures from the last 'minutes' minutes
    cursor.execute(f'''
        SELECT * FROM environment
        WHERE timestamp >= DATETIME('now', ?)
    ''', (f'-{minutes} minutes',))
    return cursor.fetchall()
    conn.close()    


#                                                             #
# environment ### environment ### environment ### environment #
#                                                             #


# Function to insert a new temp reading with automatic timestamp
def create_new_temp_reading(Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht):
    # Connect to the database
    # conn = sqlite3.connect("example.db")
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()
    '''
    Aqi Tvoc Eco2 Rhens Eco2rating Tvocrating Tempens Tempaht Rhaht
    '''
    cursor.execute('''
        INSERT INTO environment (Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht))
    conn.commit()
    conn.close()


#                                                     #
# EMPLOYESS ### EMPLOYESS ### EMPLOYESS ### EMPLOYESS #
#                                                     #


# Function to insert a employee with automatic timestamp
def create_new_employee(name, tagid, salary, otlimit, otform):
    # Connect to the database
    # conn = sqlite3.connect("example.db")
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()
    '''
    - id - float/REAL: Standard ID som laves i DB automatisk (autoincrement). 
    Bruges også til at finde underdatabasen til hver ansat
    - tagid - string/TEXT: RFID tag id. 
    - name - string: Navn til lettere genkendelse i systemet
    - salary - float: Timelånen opgivet i kr i timen, eg "185" for 185 dkk i timen
    - otlimit - float: Hvornår skal der betales OT (Overtime). Opgiv i timer, fx 6 timer, hvorefter der betales ot
    - otform - float: 50% ekstra i lån, 100% etc. Opgiv i procent, fx "50" for 50% ekstra i overtid
    - timestamp for oprettelse i systemet
    '''
    cursor.execute('''
        INSERT INTO main (name, tagid, salary, otlimit, otform)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, tagid, salary, otlimit, otform))
    conn.commit()
    conn.close()

def fetch_employees():
    # Connect to the database
    # conn = sqlite3.connect("example.db")
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()


    # Query to get employees names from main DB
    cursor.execute(f'''
        SELECT name FROM main
    ''')
    cluttered_names = cursor.fetchall()
    for i in range(len(cluttered_names)):
        print(f"Employee nr. {i} : {cluttered_names[i][0]}")
    conn.close()
def check_employee_session(name):
    # Connect to the database
    # conn = sqlite3.connect("example.db")
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()

    '''Query to check employee session'''
    cursor.execute(f'''
        SELECT id FROM sessions
        WHERE name = ?
        AND endtimestamp IS NULL
        LIMIT 1;
    ''', (f'{name}',))
    return cursor.fetchall()
    conn.close()
def convert_uid_to_name(uid):
    '''
    Converts a UID to a name, if its present in DB
    '''
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM main WHERE tagid = ?", (uid,))
    result = cursor.fetchone()
    return result
    conn.close()

def sessionupdate(name):
    '''
    Session administration. Runs a check to see if a session is currently active. If so, it ends that session, if not, it starts a new session
    '''
    print("\n----------\n")

    # Connect to the database
    # conn = sqlite3.connect("example.db")
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()


    check = check_employee_session(name)

    if len(check) == 0: #Function to insert a starting session for employee
        print(f"Starting new session for employee {name}")
        # Gathering information from main-db about the employee
        cursor.execute(f'''
            SELECT * FROM main
            WHERE name == ?
        ''', (f'{name}',))
        info_from_main = cursor.fetchall()
        # [(1, 'Anders', 'A', 100.0, 6.0, 50.0, '2025-05-04 10:48:16')]
        # info_from_main is a list. 0 accesses the first element of the list, containing a tuple. [3] accesses the forth element (salary)
        salary = info_from_main[0][3]
        othours = info_from_main[0][4]
        otform = info_from_main[0][5]
        # Partial info writing to DB
        cursor.execute('''
            INSERT INTO sessions (name, salary, othours, otform)
            VALUES (?, ?, ?, ?)
        ''', (name, salary, othours, otform))
        conn.commit()

    if len(check) == 1: #Function to end session
        print(f"\nEnding session for {name}!\n")
        # Function to fetch timestamp from sessions DB. Used to calculate OT and paycheck
        cursor.execute('''
            SELECT id, starttimestamp, othours, otform, salary FROM sessions
            WHERE name = ? AND endtimestamp IS NULL
        ''', (f'{name}',))
        current_session = cursor.fetchall()
        # [(10, '2025-05-04 16:49:48', 6.0, 50.0, 100.0)]
        # current_session is a list of tuples. We are only expecting one hit
        # We are accessing the first element of the list (A tuple), and in that element, we are accessing the second item (Datetime)
        # DONT touch tzinfo = timezone.utc. Its to make sure that all timezones are in UTC, but it took a long time to get working, so dont touch
        start = datetime.fromisoformat(current_session[0][1]).replace(tzinfo=timezone.utc)
        salary = current_session[0][4]
        otform = current_session[0][3]
        othours = current_session[0][2]
        end = datetime.now(timezone.utc)
        # delta is a datetime.timedelta class, it can return its value in seconds, by calling its seconds function
        delta = end - start
        min_worked = int(delta.total_seconds() / 60 + 1)
        hours_worked = round(min_worked/60, 2)
        otpaid = 0
        print(f"Hours worked! {hours_worked}")
        if hours_worked >= othours:
            othours = hours_worked - othours
            otpaid = othours * otform
        print(f"OThours: {othours}")
        print(f"OTform: {otform}")
        print(f"OTPaid: {otpaid}")
        paid = hours_worked * salary + otpaid
        print(f"Paid: {paid}")
        # We want to update endtimestamp, hours, paid
        # Updating the partial DB write from earlier function
        cursor.execute('''
            UPDATE sessions 
            SET endtimestamp = ?, hours = ?, paid = ?
            WHERE name = ? AND endtimestamp IS NULL
        ''', (end, hours_worked, paid, name))
        conn.commit()
    print("\n----------")
    conn.close()