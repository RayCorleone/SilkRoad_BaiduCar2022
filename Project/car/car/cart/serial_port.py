"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-09
 @Version   v0.0
 @Function  串行接口控制类
 @Comment   None
"""

import time
import serial
from threading import Lock

from car.config import CONTROLLER


class MySerial:
    def __init__(self):
        port_x = "/dev/ttyUSB0"
        # bps = 115200
        if CONTROLLER == "mc601":
            bps = 380400
        elif CONTROLLER == "wobot":
            bps = 115200
        else:
            bps = 115200
        self.res = None
        self.serial = serial.Serial(port_x, int(bps), timeout=0.004, parity=serial.PARITY_NONE, stopbits=1)
        time.sleep(1)

    def write(self, data):
        lock = Lock()
        lock.acquire()
        try:
            self.serial.write(data)
            # print(data)
            self.serial.flush()
            self.res = self.serial.readline()
            for i in range(10):
                if(self.res[-2:] == b'\r\n'):
                    break;
                else:
                    self.res = self.res + self.serial.readline()
            # print(self.res)
            self.serial.flush()
            
        except ZeroDivisionError as e:
            print('except:', e)
        finally:
            # print("serial.write_finally\n")
            lock.release()
            pass

    def read(self):
        return self.res
