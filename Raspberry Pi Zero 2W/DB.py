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
conn.close()


# Function to insert a value reading with automatic timestamp
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


# Function to fetch all readings
def fetch_all_temperatures():
    # Connect to the database
    # conn = sqlite3.connect("example.db")
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM main")
    return cursor.fetchall()
    conn.close()

def fetch_temperatures_last_x_minutes(minutes):
    # Connect to the database
    # conn = sqlite3.connect("example.db")
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()

    # Query to get temperatures from the last 'minutes' minutes
    cursor.execute(f'''
        SELECT * FROM main
        WHERE timestamp >= DATETIME('now', ?)
    ''', (f'-{minutes} minutes',))
    return cursor.fetchall()
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

'''
while True:
    print(f"\nWhat do you want to do?\n1: Exit\n2: Create new employee\n3: Show main DB\n4: Sessions")
    select = int(input("Chosse a number: "))
    print("\n----------\n")
    if select == 1:
        break
    if select  == 2:
        print(f"adding new employee\nType tagID as a string/TEXT:")
        tagid = input()
        print(f"adding new employee\nType name as a string/TEXT:")
        name = input()
        print(f"adding new employee\nType salary as a float/REAL:")
        salary = float(input())
        print(f"adding new employee\nType OTlimit as a float/REAL. 6 = after 6 hours, overtime is begun:")
        otlimit = float(input())
        print(f"adding new employee\nType salary as a float/REAL. 50 = 50% after OTlimit is reached")
        otform = float(input())
        create_new_employee(name, tagid, salary, otlimit, otform)
    if select == 3:
        print("Employee added last 2 minuttes", fetch_temperatures_last_x_minutes(2))
        print("Total number of employees",fetch_all_temperatures())
    if select == 4:
        fetch_employees()
        print("Name employee for session:")
        name = input()
        sessionupdate(name) #There should be a function to update a tag from tagid to name,
'''

