import DB

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/send', methods=['POST'])
def receive_data():
    data = request.get_json()
    print("Received from ESP32:", data)
    # create_new_employee(name, tagid, salary, otlimit, otform)
    # DB.create_new_employee("Bo", "0x53fcc401", 200, 5, 100)
    # Check to see if UID match anyone in the DB
    print(DB.fetch_all_temperatures())
    uid = data["value"]
    print(uid)
    print(type(uid))
    print(DB.convert_uid_to_name(uid))

    # Send back a simple response
    response = {"message": "Hello ESP32, got your value: " + str(data['value'])}
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
