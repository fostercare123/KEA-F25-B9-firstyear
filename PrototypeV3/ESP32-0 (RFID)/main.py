from machine import Pin, SoftSPI, PWM, ADC
from mfrc522 import MFRC522
from gpio_lcd import GpioLcd
import urequests
import _thread
import time

sck = Pin(18, Pin.OUT)
copi = Pin(23, Pin.OUT)
cipo = Pin(19, Pin.OUT)
try:
    spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=copi, miso=cipo)
    sda = Pin(21, Pin.OUT)
    reader = MFRC522(spi, sda)
except Exception as e:
    print(f"SPI Initialization Error: {e}")
    
lcd = GpioLcd(rs_pin=Pin(27), enable_pin=Pin(25),
              d4_pin=Pin(33), d5_pin=Pin(32), d6_pin=Pin(16), d7_pin=Pin(22),
              num_lines=4, num_columns=20)

Backlight = Pin(12, Pin.OUT)
Backlight.value(1)

card_3 = "0x3d913304"
card_5 = "0x53fcc401"
card_6 = "0x64d2c401"

screen_state = "home"

def buzzer(pin_number,frequency,duty):
    pwm = PWM(Pin(pin_number))
    pwm.freq(frequency)
    pwm.duty(duty)
    return pwm

def pos_scan_np():
    buzzer(13,1000,100)
    time.sleep(0.1)
    buzzer(13,1000,0)

print('Ready to read')
print('')

def home_screen():
    global screen_state
    lcd.clear()
    lcd.move_to(0, 1)
    lcd.putstr('    Welkomen til')
    lcd.move_to(0, 2)
    lcd.putstr('      Gordion')
    screen_state = "home"
home_screen()

#######################
# Global flag
# Important for in case of timeout when sending data
# Used for the second thread handeling the sending and reciving data part
# Used by "threaded_request" which tells if it has recived any data
# Used by "com_raspi" to kill "threaded_request" in case it has frozen (eg no ack reviced)
request_done = False
response_data = None

# URL for Raspberry pi running DB

url = "http://192.168.156.43:5000/send"
headers = {"Content-Type": "application/json"}

def threaded_request(data):
    global request_done, response_data
    # Using global vars
    try:
        response = urequests.post(url, json=data, headers=headers)
        # This is the headers where data is send
        response_data = response.json() # Response which is written in response_data
        response.close()
    except Exception as e:
        response_data = f"Error: {e}"
    request_done = True

def com_raspi(data_to_send, timeout=5):
    global request_done, response_data
    request_done = False
    response_data = None
    print("#################")
    # Starting function in own thread, to make sure it dosent freeze up the whole ESP
    _thread.start_new_thread(threaded_request, (data_to_send,))
    
    start = time.ticks_ms() #Basic non-blocking delay
    while not request_done:
        # Clock to check how long the process has been running.
        # Converting Seconds to MS to compare to ticks_ms
        if time.ticks_diff(time.ticks_ms(), start) > timeout * 1000:
            print("Request timed out")
            return None
        time.sleep(0.1) # Idk, im just kind to the ESP
    time_to_respond = (time.ticks_ms() - start) / 1000 # Response time calc.
    print("Response took:", time_to_respond, "seconds") 
    return response_data
#######################

while True:
    try:
        (status, tag_type) = reader.request(reader.CARD_REQIDL)
        
        global rasp_data
        
        if status == reader.OK:
            (status, raw_uid) = reader.anticoll()
            lcd.clear()
            pos_scan_np()
            
            if status == reader.OK:
                lcd.move_to(0, 1)
                lcd.putstr('  Vent Venligst...')
                print('New Card Detected')
                print('  - Tag Type: 0x%02x' % tag_type)
                uid_str = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                print('  - uid: ', uid_str)
                print('')
                my_dict = {
                            "UID": uid_str,
                            "ID": 0,
                            "ERRORS": 0
                        }
                data = com_raspi(my_dict)
                print(data)
                try:
                    lcd.clear()
                    if int(data.get("Min")) == 0:
                        lcd.putstr("Welcome, " + data.get("Name"))
                    else:
                        lcd.putstr("Goodbye, " + data.get("Name"))
                    
                except:
                    pass
                
                time.sleep(2)
                home_screen()
                
                if reader.select_tag(raw_uid) == reader.OK:
                    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                    if reader.auth(reader.AUTH, 8, key, raw_uid) == reader.OK:
                        print("Address Data: %s" % reader.read(8))
                        reader.stop_crypto1()
        
                        
                    else:
                        print("AUTH ERROR")
                else:
                    print("FAILED TO SELECT TAG")                
    except KeyboardInterrupt:
        print("\nExiting program!")
        Backlight.value(0)
        break
