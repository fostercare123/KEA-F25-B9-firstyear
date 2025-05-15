from machine import I2C, Pin
from time import sleep, ticks_ms, ticks_diff
import json
import urequests
import neopixel
import _thread
from ens160 import ENS160
from ahtx0 import AHT20

# Initialize I2C
i2c = I2C(0, scl=Pin(26), sda=Pin(25), freq=100000)

# Initialize sensors
ens = ENS160(i2c)
aht = AHT20(i2c)

# NeoPixel setup
np = neopixel.NeoPixel(Pin(5), 3)

# Raspberry Pi endpoint
url = "http://192.168.156.9:5000/send"
headers = {"Content-Type": "application/json"}

# --- Functions ---

def read_sensors():
    temp_aht = aht.temperature
    rh_aht = aht.relative_humidity

    # Læs ENS160 værdier
    aqi, tvoc, eco2, temp_ens, rh_ens, eco2_rating, tvoc_rating = ens.read_air_quality()

    # Lav dictionary med alle data
    sensor_data = {
        "Aqi": aqi,
        "Tvoc": tvoc,
        "Eco2": eco2,
        "Temp_ens": temp_ens,
        "Rh_ens": rh_ens,
        "Eco2_rating": eco2_rating,
        "Tvoc_rating": tvoc_rating,
        "Temp_aht": round(temp_aht, 2),
        "Rh_aht": round(rh_aht, 2),
        "ID": 1,
        "ERRORS": 0
    }

    # Print for test
    print(f"AHT21 Temp: {temp_aht:.2f}°C, RH: {rh_aht:.2f}%")
    print(f"ENS160 AQI: {aqi}, TVOC: {tvoc} ppb, eCO2: {eco2} ppm")
    print(f"ENS160 Rating: eCO2 -> {eco2_rating}, TVOC -> {tvoc_rating}")
    print("-----")

    return sensor_data


def threaded_request(data):
    global request_done, response_data
    try:
        response = urequests.post(url, json=data, headers=headers)
        response_data = response.json()
        response.close()
    except Exception as e:
        response_data = f"Error: {e}"
    request_done = True

def com_raspi(data_to_send, timeout=5):
    global request_done, response_data
    request_done = False
    response_data = None

    _thread.start_new_thread(threaded_request, (data_to_send,))
    start = ticks_ms()
    while not request_done:
        if ticks_diff(ticks_ms(), start) > timeout * 1000:
            print("Request timed out")
            return None
        sleep(0.1)
    print("Response took:", (ticks_ms() - start) / 1000, "seconds")
    return response_data

"""
def indicate_success(success):
    np[0] = (0, 255, 0) if success else (255, 0, 0)
    np.write()
    sleep(1)
    np[0] = (0, 0, 0)
    np.write()
"""
# --- Main Loop ---

while True:
    sensor_data = read_sensors()
    response = com_raspi(sensor_data)
    success = response is not None
    # indicate_success(success)
    sleep(10)

