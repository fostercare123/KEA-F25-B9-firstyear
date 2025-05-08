from machine import Pin, SoftSPI, PWM, ADC
from time import sleep
from mfrc522 import MFRC522
from neopixel import NeoPixel
from gpio_lcd import GpioLcd

sck = Pin(18, Pin.OUT)
copi = Pin(23, Pin.OUT)
cipo = Pin(19, Pin.OUT)

spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=copi, miso=cipo)
sda = Pin(21, Pin.OUT)
reader = MFRC522(spi, sda)

lcd = GpioLcd(rs_pin=Pin(27), enable_pin=Pin(25),
              d4_pin=Pin(33), d5_pin=Pin(32), d6_pin=Pin(16), d7_pin=Pin(22),
              num_lines=4, num_columns=20)

Backlight = Pin(12, Pin.OUT)
Backlight.value(1)
"""
lys = ADC(Pin(34))   # Use GPIO34 (input only)
lys.atten(ADC.ATTN_11DB)  # Full range: 0 - 3.6V
lys.width(ADC.WIDTH_12BIT)  # Resolution: 0 - 4095
"""
num_pixels = 3
neo_pin = Pin(15, Pin.OUT)
np = NeoPixel(neo_pin, num_pixels)

card_3 = "0x3d913304"
card_5 = "0x53fcc401"
card_6 = "0x64d2c401"


def buzzer(pin_number,frequency,duty):
    pwm = PWM(Pin(pin_number))
    pwm.freq(frequency)
    pwm.duty(duty)
    return pwm

def pos_scan_np():
    np[0] = (0,30,0)
    np[1] = (0,30,0)
    np[2] = (0,30,0)
    np.write()
    buzzer(13,1000,512)
    sleep(0.1)
    buzzer(13,1000,0)
    
print('Ready to read')
print('')

lcd.move_to(0, 0)
lcd.putstr('Welkomen til')
lcd.move_to(0, 1)
lcd.putstr('Gordion')
sleep(1)

while True:
    try:
        np[0] = (30,0,0)
        np[1] = (30,0,0)
        np[2] = (30,0,0)
        np.write()
        """
        value = lys.read()
        print(value)
        """
        (status, tag_type) = reader.request(reader.CARD_REQIDL)
        if status == reader.OK:
            (status, raw_uid) = reader.anticoll()
            lcd.clear()
            pos_scan_np()
            
            if status == reader.OK:
                print('New Card Detected')
                print('  - Tag Type: 0x%02x' % tag_type)
                uid_str = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                print('  - uid: ', uid_str)
                print('')
                
                if uid_str == card_3:
                    print("welcome user 3")
                    lcd.move_to(0, 1)
                    lcd.putstr('   welcome user 3')
                    
                if uid_str == card_5:
                    print("welcome user 5")
                    lcd.move_to(0, 1)
                    lcd.putstr('   welcome user 5')
                    
                if uid_str == card_6:
                    print("welcome user 6")
                    lcd.move_to(0, 1)
                    lcd.putstr('   welcome user 6')
                
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
        np[0] = (0,0,0)
        np[1] = (0,0,0)
        np[2] = (0,0,0)
        np.write()
        break
