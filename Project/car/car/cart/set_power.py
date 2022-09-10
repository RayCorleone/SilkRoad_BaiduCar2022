"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-09
 @Version   v1.0
 @Function  关闭机器省电
 @Comment   None
"""

import time

from car.component import serial, buzzer


# 关闭机器省电
def start_machine():
    cmd_data = bytes.fromhex('77 68 03 00 02 67 0A')
    for i in range(0, 2):
        serial.write(cmd_data)
        time.sleep(0.2)


if __name__ == "__main__":
    start_machine()
    buzzer.rings()
    time.sleep(0.1)
