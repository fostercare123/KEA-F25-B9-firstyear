import DB # All DB-related things go here!
import graphs # Graph stuff goes here
import threading
import base64 # Graphs and graphics


from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO # Websockets

from io import BytesIO # Graphs and stuff

from time import sleep

app = Flask(__name__)
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

@app.route('/login')
def login():
    return render_template('login.html')



# 
# Important stuff, dont touch.....
# 

# Emit loop, that updates the graphs every 5 seconds
def update_graphs():
    # Temp Graph
    graph_img = graphs.create_graph(9,10, 90) #See graph.datanames for explanation
    if graph_img:
        socketio.emit('temp_graph', {'image': graph_img})
    # Air Graph
    graph_img = graphs.create_graph(3,4, 90) #See graph.datanames for explanation
    if graph_img:
        socketio.emit('CO2TVOCgraph', {'image': graph_img}) 
def emit_loop():
    while True: 
        update_graphs()
        sleep(4)


@app.route('/send', methods=['POST'])
def receive_data():
    data = request.get_json()
    print("---------- New Post Request ----------")
    print(f"This is of datatype: {type(data)} .Raw data that was sent:")
    # create_new_employee(name, tagid, salary, otlimit, otform)
    # DB.create_new_employee("Bo", "0x53fcc401", 200, 5, 100)
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
        DB.create_new_temp_reading(data['Aqi'], data['Tvoc'], data['Eco2'], data['Rh_ens'], data['Eco2_rating'], data['Tvoc_rating'], data['Temp_ens'], data['Temp_aht'], data['Rh_aht'])
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
    return jsonify(response)

if __name__ == '__main__':
    threading.Thread(target=emit_loop, daemon=True).start() #Starts Sensor Loop with threading enabled
    socketio.run(app, host='0.0.0.0', port=5000)