# Esp32-id-2-fan-main-v1-1

### Imports ###
from bluetooth import BLE
import ubluetooth
import Esp32_id_2_fan_backend_v1  

### WiFi og netværk ###
SSID = "Your_SSID"
PASSWORD = "hey"

print(f"SSID: {SSID}, PASSWORD: {PASSWORD}") # test

# get form weside
fan_ha = 1  # Fan speed control 0 to 2 
fan_control = 1 # Fan on 1 or off 0

print(f"fan_ha: {fan_ha}, fan_control: {fan_control}") # test

### Fan speed logic ###
if fan_ha == 0:
    speed = 50
elif fan_ha == 1:
    speed = 50  
else:
    speed = 200
print(f"Fan speed set to {speed}") # test

### Motor control ###
if fan_control == 1:
    Esp32_id_2_fan_backend_v1.motor_forward(speed) # Start motor
    print("Motor started") # test
else:
    Esp32_id_2_fan_backend_v1.motor_stop() # Stop motor
    print("Motor stopped") # test
    
    
    
### Bluetooth ## kun noget for sjovt
    
# Set up BLE (Bluetooth Low Energy) for communication
ble = BLE()
ble.active(True)

# A simple Bluetooth setup with basic advertising 
def ble_irq(event, data):
    """Callback function to handle BLE events (like connection and data reception)."""
    if event == ubluetooth.CLIENT_CONNECTED:
        print("Bluetooth client connected")
    elif event == ubluetooth.CLIENT_DISCONNECTED:
        print("Bluetooth client disconnected")

# Example: Start advertising (advertising for a simple BLE peripheral)
ble.config(gap_name="ESP32_Fan_Control")
ble.gap_advertise(100, adv_data=b"\x02\x01\x06\x03\x03\xAA\xFE\x0A\x09ESP32 Fan")

# BLE event loop (to listen for events like Bluetooth connection)
while True:
    ble.wait_for_event()