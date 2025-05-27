import urequests
import time
import random
import _thread

from machine import Pin, SoftSPI
from mfrc522 import MFRC522

# Imports ^^^

# Card Reader imports. Using SPI
# This is the pins used by the cardreader on the small test-board
sck = Pin(18, Pin.OUT)
copi = Pin(23, Pin.OUT) # Controller out, peripheral in
cipo = Pin(19, Pin.OUT) # Controller in, peripheral out
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=copi, miso=cipo)
sda = Pin(21, Pin.OUT)
reader = MFRC522(spi, sda)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
#																											#
# From here and down, data is sent to the Raspiberry Pi. All over this (Exept imports) can be safly deleted #
#																											#
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #

# Global flag
# Important for in case of timeout when sending data
# Used for the second thread handeling the sending and reciving data part
# Used by "threaded_request" which tells if it has recived any data
# Used by "com_raspi" to kill "threaded_request" in case it has frozen (eg no ack reviced)
request_done = False
response_data = None
# URL for Raspberry pi running DB
url = "http://192.168.156.9:5000/send"
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
    time_to_respond = (ticks_ms() - start) / 1000 # Response time calc.
    print("Response took:", time_to_respond, "seconds") 
    return response_data

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
#																											#
# From here and up, data is sent to the Raspiberry Pi. All code under this can be safly deleted             #
#																											#
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #

# Main loop
#if __name__ == "__main__"
while True: #ONLY HANDELING THE TAG SCANNER!
    try:
        (status, tag_type) = reader.request(reader.CARD_REQIDL)
        # This is like typing:
        #response = reader.request(reader.CARD_REQIDL)
        #status = response[0]
        #tag_type = response[1]
        #Its just unpacking the returned variables from the tuple, 
        #into the two variables
        #The paranthes arent strictly neccesary, but it can improve readebillaty
        if status == reader.OK:
            (status, raw_uid) = reader.anticoll()
            # Anti Collision prevents multiple reads at the same time
            # Fetches the UID (tagid) from the tag
            if status == reader.OK:
                print('New Card Detected')
                #print('  - Tag Type: 0x%02x' % tag_type)
                #print('  - uid: 0x%02x%02x%02x%02x' % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                #print('')
                uid_str = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                if reader.select_tag(raw_uid) == reader.OK:
                    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                    if reader.auth(reader.AUTH, 8, key, raw_uid) == reader.OK:
                        print("Address Data: %s" % reader.read(8))
                        reader.stop_crypto1()
                        # Own things thats not part of the example
                        print(f"Sending UID: {uid_str}")
                        my_dict = {
                            "UID": uid_str,
                            "ID": 0,
                            "ERRORS": 0
                        }
                        received = com_raspi(my_dict)
                        print("Received:", received)
                    else:
                        print("AUTH ERROR")
                else:
                    print("FAILED TO SELECT TAG")
    except KeyboardInterrupt:
        break

