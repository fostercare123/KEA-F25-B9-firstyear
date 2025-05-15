import DB

from flask import Flask, request, jsonify

app = Flask(__name__)

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


    # Send back a simple response
    if data['ID'] == 1: # ID = 1, New Temp Reading
        print("New Temp reading recived from ESP-1")
        DB.create_new_temp_reading(data['Aqi'], data['Tvoc'], data['Eco2'], data['Rh_ens'], data['Eco2_rating'], data['Tvoc_rating'], data['Temp_ens'], data['Temp_aht'], data['Rh_aht'])
    response = {"message": "Hello ESP32, got your value: " + str(data)}
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
