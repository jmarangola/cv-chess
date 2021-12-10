from serial import Serial
from time import sleep

PORT = "/dev/tty.usbmodem101396701"


def send_wait_for_tx(ser, resp_msg, maxIterations=1000, port=PORT, delay=0.01):
    i = 0
    while True:
        res = ser.readline().decode()
        if i == maxIterations:
            print("Maximum iterations reached. Exiting wait_for_response: -1")
            return False
        if res == resp_msg:
            return True
        sleep(delay)
        i+=1

with Serial(PORT, 57600, timeout=1) as ser:

