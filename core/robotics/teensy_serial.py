import serial
from time import sleep

PORT = "/dev/tty.usbmodem101396701"

def send_wait_for_tx(ser, resp_msg, maxTimeMS=60000, port=PORT, delay=0.001):
    i = 0
    while True:
        res = ser.readline().decode()
        if i >= maxTimeMS:
            print("Maximum iterations reached. Exiting wait_for_response: -1")
            return False
        if res == resp_msg:
            return True
        sleep(delay)
        i += delay
        
def send_serial(raw_position):
    with serial.Serial() as ser:
        ser.port="/dev/tty.usbmodem101396701"
        ser.baudrate = 115200
        ser.open()
        tx = ",".join(raw_position) + "\n"
        tx = tx.encode()
        ser.write(tx)
        ser.flush()
        rx = ser.readline()
        send_wait_for_tx(ser, "recd")
