from machine import Pin, PWM
from time import sleep

### Pin-only ###
# P12=Pin(12,Pin.OUT)
# P13=Pin(13,Pin.OUT)
# while True:
#     P12.value(1)
#     P13.value(0)
#     sleep(1)
#     P12.value(0)
#     P13.value(1)
#     sleep(1)

### PWM ###
# P12=PWM(Pin(12,Pin.OUT),freq=1,duty=1023)
# P13=PWM(Pin(13,Pin.OUT),freq=1,duty=1023)
# while True:
#     P13.freq(1)
#     P12.freq(5000)
#     sleep(1)
#     P12.freq(1)
#     P13.freq(512)
    
# P12=PWM(Pin(12,Pin.OUT),freq=512,duty=512)
# P13=PWM(Pin(13,Pin.OUT),freq=512,duty=512)
# while True:
#     P13.duty(0)
#     P12.duty(512)
#     sleep(1)
#     P12.duty(0)
#     P13.duty(512)

pin=PWM(Pin(12,Pin.OUT),freq=50,duty=0)
while True:
    pin.duty(512)
    sleep(1)
    pin.duty(256)
    sleep(1)