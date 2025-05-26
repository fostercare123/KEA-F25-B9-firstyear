from machine import Pin, PWM
import time
import urequests
import _thread

# Motor control pins
in1 = Pin(17, Pin.OUT)
in2 = Pin(0, Pin.OUT)

def forward():
    in1.value(1)
    in2.value(0)

def backward():
    in1.value(0)
    in2.value(1)

def stop():
    in1.value(0)
    in2.value(0)
    
# Global flag
# Important for in case of timeout when sending data
# Used for the second thread handeling the sending and reciving data part
# Used by "threaded_request" which tells if it has recived any data
# Used by "com_raspi" to kill "threaded_request" in case it has frozen (eg no ack reviced)
request_done = False
response_data = None

# URL for Raspberry pi running DB

url = "http://192.168.156.211:5000/send"
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

switch = 0
while True:
    data_to_send = {
        "ID":2,
        "ERRORS":0
        }
    motor_data = com_raspi(data_to_send)
    print(motor_data)
    if motor_data is not None and "motor_on" in motor_data:
        switch = motor_data["motor_on"]
    if switch == 1:
        forward()
    else:
        stop()
        

    time.sleep(1)
        
