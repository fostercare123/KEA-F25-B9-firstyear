import machine
import time
import json
import urequests
import neopixel
from ens160 import ENS160
from ahtx0 import AHT21

# --- SENSOR KONFIGURATION ---

# I2C til ENS160 og AHT21 (begge på samme bus)
i2c = machine.I2C(0, scl=machine.Pin(26), sda=machine.Pin(25))

# ENS160 luftkvalitet
ens = ENS160(i2c)
ens.set_operating_mode(ENS160.MODE_STANDARD)

# AHT21 temperatur og fugt
aht = AHT21(i2c)

# KY-018 LDR på ADC-pin
ldr_pin = machine.ADC(machine.Pin(36))
ldr_pin.atten(machine.ADC.ATTN_11DB)  # Rækkevidde (0-3.3V)

# NeoPixel setup
np = neopixel.NeoPixel(machine.Pin(5), 1)  # GPIO5, 1 LED

# Raspberry Pi endpoint
PI_URL = "http://your-raspberrypi-ip:port/send"  # SKRIV AKTUELLE IP og PORT

# --- FUNKTIONER ---

def read_sensors():
    temp, hum = aht.read()
    air_quality = ens.get_air_quality_index()
    ldr_value = ldr_pin.read()
    return {
        "temperature": round(temp, 2),
        "humidity": round(hum, 2),
        "air_quality_index": air_quality,
        "light_level": ldr_value
    }

def save_json(data, filename="sensor_data.json"):
    with open(filename, "w") as f:
        json.dump(data, f)

def send_to_pi(data):
    headers = {"Content-Type": "application/json"}
    try:
        response = urequests.post(PI_URL, data=json.dumps(data), headers=headers)
        print("Server response:", response.text)
        response.close()
        return True
    except Exception as e:
        print("Failed to send:", e)
        return False

def indicate_success(success):
    np[0] = (0, 255, 0) if success else (255, 0, 0)
    np.write()
    time.sleep(1)
    np[0] = (0, 0, 0)
    np.write()

# --- MAIN LOOP ---

while True:
    sensor_data = read_sensors()
    print("Read sensor data:", sensor_data)

    save_json(sensor_data)
    success = send_to_pi(sensor_data)
    indicate_success(success)

    time.sleep(60)  # Vent 1 min før næste læsning
