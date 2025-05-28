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
conn = sqlite3.connect('example.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM main WHERE name = 'Anders'")
if not cursor.fetchone():
    cursor.execute(
        "INSERT INTO main (name, tagid, salary, otlimit, otform) VALUES (?, ?, ?, ?, ?)",
        ('Anders', '0x53fcc401', 100.0, 5.0, 50.0)
    )
    cursor.execute(
        "INSERT INTO main (name, tagid, salary, otlimit, otform) VALUES (?, ?, ?, ?, ?)",
        ('Ben', '0x3d913304', 500.0, 1.0, 200.0)
    )
    cursor.execute(
        "INSERT INTO main (name, tagid, salary, otlimit, otform) VALUES (?, ?, ?, ?, ?)",
        ('Tristan', '0x64d2c401', 2000.0, 10.0, 50.0)
    )
conn.commit()


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
        paid REAL,
        notes TEXT
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
        Rhaht REAL,
        LDR REAL
    )
''')
# Api Tvoc Eco2 Rhens Eco2rating Tvocrating Tempens Tempaht Rhaht
# Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht



### Errors table!
cursor.execute('''
    CREATE TABLE IF NOT EXISTS errors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        machine TEXT,
        errortype TEXT,
        erroramount REAL,
        errormessage TEXT
    )
''')


### Empty tags table! unallocatedtags
cursor.execute('''
    CREATE TABLE IF NOT EXISTS unallocatedtags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        UID TEXT
    )
''')


conn.close() #THIS BIT LAST!!!

# ESP 2 funtions

def fetch_latest_AQI():
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()
    # Vælger aqi fra environment-tabellen i example.db, sortere efter timestamp, og sætter i rækkefølge
    cursor.execute("SELECT aqi FROM environment ORDER BY timestamp DESC LIMIT 1")
    aqi = cursor.fetchone()[0]
    print(aqi)
    print(type(aqi))
    conn.close()
    return(aqi)
# Unknow tags functions

def report_new_unknown_tag(UID):
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()
    '''
    Function to add new unknown unallocated tag, or update time for existing tag in this table. UID
    '''

    '''Query to check to see if UID is already in DB, in which case its timestamp should be updated'''
    cursor.execute(f'''
        SELECT id FROM sessions
        WHERE UID = ?;
    ''', (f'{UID}',))
    checkUID = cursor.fetchall()
    print(checkUID)
    print(type(checkUID))
    if checkUID == 0:
        cursor.execute('''
            INSERT INTO unallocatedtags (UID)
            VALUES (?)
        ''', (UID))
        conn.commit()
        conn.close()
        print(f"New unknow tag added. UID: {UID}")
def fetch_all_unallocated_tags():
    pass

# Error functions

def report_error(machine, errortype, erroramount = None, errormessage = None):
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()
    '''
    machine, errortype, erroramount, errormessage
    '''
    cursor.execute('''
        INSERT INTO errors (machine, errortype, erroramount, errormessage)
        VALUES (?, ?, ?, ?)
    ''', (machine, errortype, erroramount, errormessage))
    conn.commit()
    conn.close()
    print(f"X---X---X---X---X---X---X\nNew error reported!\nError happend on machine: {machine}\nErrortype was: {errortype}\nThe error happend {erroramount} times\nErrormessage was: {errormessage}\nX---X---X---X---X---X---X")

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
def create_new_temp_reading(Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht, LDR):
    # Connect to the database
    # conn = sqlite3.connect("example.db")
    conn = sqlite3.connect("example.db", check_same_thread=False)
    cursor = conn.cursor()
    '''
    Aqi Tvoc Eco2 Rhens Eco2rating Tvocrating Tempens Tempaht Rhaht
    '''
    cursor.execute('''
        INSERT INTO environment (Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht, LDR)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht, LDR))
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
    print("Convert UID to Name")
    print(result)
    print(type(result))
    print(result[0])
    print(type(result[0]))
    print("-------------------")
    return result[0]
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
        print("This is the info_from_main var. being printed:")
        print(info_from_main)
        print(type(info_from_main))
        print("--------------------------")
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
        response = {
            "Name": name,
            "Min": 0,
            "Paid": 0
        }
        return(response)

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
        response = {
            "Name": name,
            "Min": min_worked,
            "Paid": paid
        }
        return(response)
    print("\n----------")
    
    conn.close()