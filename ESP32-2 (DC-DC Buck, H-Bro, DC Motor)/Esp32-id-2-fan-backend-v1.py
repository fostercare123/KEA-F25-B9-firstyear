# Esp32-id-2-fan-backend-v1-1

### Imports ###
from machine import Pin, PWM, reset
from time import ticks_ms
from main import speed, SSID, PASSWORD
import gc
import network

# Define PWM frequency and duty cycle
freq_r = 50
duty_r = 0
freq_l = 50
duty_l = 0

# Set up motor control pins
P12 = Pin(12, Pin.OUT)
P13 = Pin(13, Pin.OUT)

# Initialize PWM channels on the correct pins
pin_r = PWM(P12, freq=freq_r, duty=duty_r)
pin_l = PWM(P13, freq=freq_l, duty=duty_l)

# Motor forward with variable speed
def motor_forward(speed):
    speed = max(0, min(1023, speed))
    pin_r.duty(speed)
    pin_l.duty(0)

# Motor reverse with variable speed
def motor_reverse(speed):
    speed = max(0, min(1023, speed))
    pin_l.duty(speed)
    pin_r.duty(0)
    
# Stop motoren
def motor_stop():
    pin_r.duty(0)
    pin_l.duty(0)

# Connect to WiFi
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print('WLAN active')

    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(SSID, PASSWORD)
        start = ticks_ms()
        while not wlan.isconnected():
            if ticks_ms() - start > 10000:
                print("Connection timeout.")
                reset()
    print("Connected to WiFi!")
    print("IP address:", wlan.ifconfig()[0])

    gc.collect()  # Rclear memory
    return wlan
