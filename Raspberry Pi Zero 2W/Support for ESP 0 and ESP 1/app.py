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
    print("Received from ESP32:")
    print("This is the raw data that was sent:")
    # create_new_employee(name, tagid, salary, otlimit, otform)
    # DB.create_new_employee("Bo", "0x53fcc401", 200, 5, 100)
    # Check to see if UID match anyone in the DB
    print(data)
    print("---- Data Type ----")
    print(type(data))

    # print(DB.convert_uid_to_name(uid))
    # {'ID': 1, 'Aqi': 1, 'Tvoc': 56, 'Eco2': 469, 'Rh_ens': 0.1953125, 'Eco2_rating': 'Excellent - Target level', 'Tvoc_rating': 'Good', 'Temp_ens': 276.0063, 'Temp_aht': 26.16, 'Rh_aht': 40.26, 'ERRORS': 0}

    # Function to create graph
    # (id, timestamp, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht)
    #  0 , 1        , 2  , 3   , 4   , 5    , 6         , 7         , 8      , 9      , 10
    graphs.create_graph(1)

    # Send back a simple response
    
    if data['ID'] == 1: # ID = 1, New Temp Reading
        print("New Temp reading recived from ESP-1")
        DB.create_new_temp_reading(data['Aqi'], data['Tvoc'], data['Eco2'], data['Rh_ens'], data['Eco2_rating'], data['Tvoc_rating'], data['Temp_ens'], data['Temp_aht'], data['Rh_aht'])
    if data['ID'] == 0: # ID = 0, New UID tag recived. Managening employee sessions
        response = DB.sessionupdate(DB.convert_uid_to_name(data['UID']))
        print("New UID reading recived from ESP-0")
        response["ID"] = 0
        response["Retry"] = 0
    else:
        response = {"message": "Hello ESP32, got your value: " + str(data)}
    return jsonify(response)

# Webpage / Homepage route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    threading.Thread(target=emit_loop, daemon=True).start() #Starts Sensor Loop with threading enabled
    socketio.run(app, host='0.0.0.0', port=5000)