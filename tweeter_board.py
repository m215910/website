import serial
import requests


def main():
    global ser
    Device = 'COM5'
    ser = serial.Serial(Device)

    while True:
        mess = ser.readline()
        msg_str = mess.decode('ascii')
        msg = msg_str.rstrip()
        if msg == 'Hi Pycharm!': #match message in arduino
            print("Got:", msg)
            result = requests.get("http://maria.wattsworth.net/like.json?id=19")
            print(result.json())
main()