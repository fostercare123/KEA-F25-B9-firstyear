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
    print("Received from ESP32:", data)
    print("This is the raw data that was sent:")
    # create_new_employee(name, tagid, salary, otlimit, otform)
    # DB.create_new_employee("Bo", "0x53fcc401", 200, 5, 100)
    # Check to see if UID match anyone in the DB
    print(DB.fetch_all_temperatures())
    print("DATA --- Dict --- DATA --- Dict")
    print(data)
    print("DATA --- DIct --- DATA --- Dict")

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
    response = {"message": "Hello ESP32, got your value: " + str(data)}
    return jsonify(response)

# Webpage / Homepage route
@app.route('/')
def index():
    return '''
    <html>
        <head>
            <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
        </head>
        <body>
            <h1>Sensor Value:</h1>
            <div id="value">Waiting...</div>

            <h1>Live CO2 and TVOC Graph</h1>
            <img id="CO2TVOCgraph" src="" alt="CO2 TVOC graph will appear here... ETA: 5 seconds" style="width:1200px; border:3px solid #ccc;"/>

            <h1>Live Temp Graph</h1>
            <img id="tempgraph" src="" alt="Temp-Graph will appear here... ETA: 5 seconds" style="width:1200px; border:3px solid #ccc;"/>

            <h1>Live Air Graph</h1>
            <img id="airgraph" src="" alt="Air-Graph will appear here... ETA: 5 seconds" style="width:1200px; border:3px solid #ccc;"/>

            <script>
                var socket = io();

                // Update sensor value
                socket.on('sensor_data', function(data) {
                    document.getElementById('value').innerText = data.value;
                });

                // Update CO2TVOCgraph
                socket.on('CO2TVOCgraph', function(data) {
                    document.getElementById('CO2TVOCgraph').src = 'data:image/png;base64,' + data.image;
                });

                // Update temp graph
                socket.on('temp_graph', function(data) {
                    document.getElementById('tempgraph').src = 'data:image/png;base64,' + data.image;
                });
                // Update air graph
                socket.on('air_graph', function(data) {
                    document.getElementById('airgraph').src = 'data:image/png;base64,' + data.image;
                });
            </script>
        </body>
    </html>
    '''


if __name__ == '__main__':
    threading.Thread(target=emit_loop, daemon=True).start() #Starts Sensor Loop with threading enabled
    socketio.run(app, host='0.0.0.0', port=5000)