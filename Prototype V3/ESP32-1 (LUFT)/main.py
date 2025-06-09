from machine import I2C, Pin, ADC
from neopixel import NeoPixel
from time import sleep, ticks_ms, ticks_diff
import json
import urequests
import neopixel
import _thread
from ens160 import ENS160
from ahtx0 import AHT20
from collections import deque

# Initialize I2C
i2c = I2C(0, scl=Pin(26), sda=Pin(25), freq=100000)

# Initialize sensors
ens = ENS160(i2c)
aht = AHT20(i2c)

# NeoPixel setup
pin = Pin(21, Pin.OUT)      # GPIO4 (can change to match your board)
num_pixels = 3             # Number of LEDs

# Initialize NeoPixel strip
np = NeoPixel(pin, num_pixels)

# Raspberry Pi endpoint
url = "http://192.168.156.43:5000/send"
headers = {"Content-Type": "application/json"}

# LDR
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)
ldr.width(ADC.WIDTH_12BIT)

aqi_buffer = deque([], 5)
tvoc_buffer = deque([], 5)
eco2_buffer = deque([], 5)

# --- Functions ---

loop_start = ticks_ms()
loop_timeout = 5000

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

data = read_sensors()

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

def red_alert(a):
    np[a] = (100, 0, 0)
    np.write()
        
def close_light(b):
    np[b] = (0,0,0)
    np.write()
    
def get_average(buffer):
    return sum(buffer) / len(buffer) if buffer else 0
    
# --- Main Loop ---

while True:
    try:
        if ticks_diff(ticks_ms(), loop_start) > loop_timeout:
            sensor_data = read_sensors()
            value = ldr.read()
            print("LDR:",value)
            sensor_data["LDR"]=value
            
            response = com_raspi(sensor_data)
            loop_start = ticks_ms()
            
            aqi = sensor_data["Aqi"]
            tvoc = sensor_data["Tvoc"]
            eco2 = sensor_data["Eco2"]
            
            aqi_buffer.append(aqi)
            eco2_buffer.append(eco2)
            tvoc_buffer.append(tvoc)
            
            if len(aqi_buffer) > 5:
                aqi_buffer.pop(0)
            if len(eco2_buffer) > 5:
                eco2_buffer.pop(0)
            if len(tvoc_buffer) > 5:
                tvoc_buffer.pop(0)
                
            avg_aqi = get_average(aqi_buffer)
            avg_eco2 = get_average(eco2_buffer)
            avg_tvoc = get_average(tvoc_buffer)
            
            print("Avg AQI:", avg_aqi)
            print("Avg eCO2:", avg_eco2)
            print("Avg Tvoc:", avg_tvoc)
            
            if avg_eco2 >= 1000:
                red_alert(0)
            else:
                close_light(0)
            if avg_tvoc >= 200:
                red_alert(1)
            else:
                close_light(1)
            if avg_aqi >= 5:
                red_alert(2)
            else:
                close_light(2)
            
    except KeyboardInterrupt:
        print("\nExiting program!")
        break
