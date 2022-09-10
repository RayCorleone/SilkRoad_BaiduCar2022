"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-09
 @Version   v1.0
 @Function  车辆四个轮子的控制类定义
 @Comment   self.speed不控制move速度
"""

import time
import serial

from car.config import CONTROLLER


class Chassis:

    def __init__(self):
        self.comma_head_all_motor = bytes.fromhex('77 68 0c 00 02 7a 01')
        self.comma_trail = bytes.fromhex('0A')

        self.speed = 20
        self.kx = 0.85
        portx = "/dev/ttyUSB0"
        if CONTROLLER == "mc601":
            bps = 380400
        elif CONTROLLER == "wobot":
            bps = 115200
        else:
            bps = 115200
        self.serial = serial.Serial(portx, int(bps), timeout=0.0005, parity=serial.PARITY_NONE, stopbits=1)
        self.p = 0.8
        self.slow_ratio = 0.97
        self.min_speed = 20

    def steer(self, angle):
        speed = int(self.speed)
        delta = angle * self.kx
        left_wheel = speed
        right_wheel = speed
    
        if delta < 0:
            left_wheel = int((1 + delta) * speed)
        elif delta > 0:
            right_wheel = int((1 - delta) * speed)
        self.move([left_wheel, right_wheel, left_wheel, right_wheel])

    def stop(self):
        self.move([0, 0, 0, 0])

    def move(self, speeds):
        left_front = int(speeds[0])
        right_front = -int(speeds[1])
        left_rear = int(speeds[2])
        right_rear = -int(speeds[3])
        self.min_speed = int(min(speeds))
        left_front_kl = bytes.fromhex('01') + left_front.to_bytes(1, byteorder='big', signed=True)
        right_front_kl = bytes.fromhex('02') + right_front.to_bytes(1, byteorder='big', signed=True)
        left_rear_kl = bytes.fromhex('03') + left_rear.to_bytes(1, byteorder='big', signed=True)
        right_rear_kl = bytes.fromhex('04') + right_rear.to_bytes(1, byteorder='big', signed=True)
        send_data_all_motor = (self.comma_head_all_motor + left_front_kl + right_front_kl + left_rear_kl + right_rear_kl
                               + self.comma_trail)
        self.serial.write(send_data_all_motor)
        time.sleep(0.001)

    def turn_left(self):
        speed = self.speed
        left_wheel = -speed
        right_wheel = speed
        self.move([left_wheel, right_wheel, left_wheel, right_wheel])

    def turn_right(self):
        speed = self.speed
        left_wheel = speed
        right_wheel = -speed

        self.move([left_wheel, right_wheel, left_wheel, right_wheel])

    def reverse(self):
        speed = self.speed
        self.move([-speed, -speed, -speed, -speed])
