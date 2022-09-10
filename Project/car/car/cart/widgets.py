"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-09
 @Version   v1.0
 @Function  车辆部件类定义(通信定义)
 @Comment   需要标注好每个设备的ID接口
"""

import cv2
import time
import struct
import threading

from car.cart import serial

## 按钮：
class Button:
    def __init__(self, port, buttonstr):
        self.state = False
        self.port = port
        self.buttonstr = buttonstr
        port_str = '{:02x}'.format(port)
        self.cmd_data = bytes.fromhex('77 68 05 00 01 E1 01 {} 0A'.format(port_str))

    def clicked(self):
        serial.write(self.cmd_data)
        #print(self.cmd_data)
        response = serial.read()
        #print(self.cmd_data)
        buttonclick = "no"
        # print("resp=",len(response))
        if len(response) == 9 and response[5] == 0xE1 and response[6] == self.port:
            button_byte = response[3:5] + bytes.fromhex('00 00')
            button_value = struct.unpack('<i', struct.pack('4B', *(button_byte)))[0]
            # print("button_value=%x"%button_value)
            if button_value >= 0x80 and button_value <= 0x28f:
                buttonclick = "3"
            elif button_value >= 0x300 and button_value <= 0x48f:
                buttonclick = "1"
            elif button_value >= 0x501 and button_value <= 0x6ff:
                buttonclick = "2"
            elif button_value >= 0x78f and button_value <= 0x9ff:
                buttonclick = "4"
            else:
                buttonclick
        return self.buttonstr == buttonclick

## 按钮：
class Button_angel:
    BUTTON = {"1": "01", "2": "02", "3": "03", "4": "04"}

    def __init__(self, port, button):
        self.state = False
        self.port = port
        button_str = self.BUTTON[button]
        port_str = '{:02x}'.format(port)
        self.cmd_data = bytes.fromhex('77 68 05 00 01 DB {} {} 0A'.format(port_str, button_str))

    def clicked(self):
        serial.write(self.cmd_data)
        response = serial.read()
        # print("resp=",len(response))
        if len(response) == 8 and response[4] == 0xDB and response[5] == self.port:
            button_byte = response[3]
            # print("button_byte=%x"%button_byte)
            if button_byte == 0x01:
                return True
        return False

## 限位开关：
class LimitSwitch:
    def __init__(self, port):
        self.state = False
        self.port = port
        self.state = True
        port_str = '{:02x}'.format(port)
        # print (port_str)
        self.cmd_data = bytes.fromhex('77 68 04 00 01 DD {} 0A'.format(port_str))

    def clicked(self):
        serial.write(self.cmd_data)
        response = serial.read()  # 77 68 01 00 0D 0A
        if len(response) < 8 or response[4] != 0xDD or response[5] != self.port \
                or response[2] != 0x01:
            return False
        state = response[3] == 0x01
        # print("state=",state)
        # print("elf.state=", self.state)
        clicked = False
        if state == True and self.state == True and clicked == False:
            clicked = True
        if state == False and self.state == True and clicked == True:
            clicked = False
        # print('clicked=',clicked)
        return clicked

## 超声传感器：
class UltrasonicSensor():
    def __init__(self, port):
        self.port = port
        port_str = '{:02x}'.format(port)
        self.cmd_data = bytes.fromhex('77 68 04 00 01 D1 {} 0A'.format(port_str))

    def read(self):
        serial.write(self.cmd_data)
        return_data = serial.read()
        if len(return_data) < 11 or return_data[7] != 0xD1 or return_data[8] != self.port:
            return None
        return_data_ultrasonic = return_data[3:7]
        ultrasonic_sensor = struct.unpack('<f', struct.pack('4B', *(return_data_ultrasonic)))[0]
        return int(ultrasonic_sensor)

## 伺服装置：测摄像头-1, 举旗-2
class Servo:
    def __init__(self, ID):
        self.ID = ID
        self.ID_str = '{:02x}'.format(ID)

    def servo_control(self, angle, speed):
        angle = int(angle)
        cmd_servo_data = bytes.fromhex('77 68 08 00 02 36 {}'.format(self.ID_str)) + speed.to_bytes(1, byteorder='big',
                                                                                                    signed=True) + \
                         (angle).to_bytes(3, byteorder='little', signed=True) \
                         + bytes.fromhex('0A')
        serial.write(cmd_servo_data)

## 伺服装置PWM：击打-1, 抓手-2
class Servo_pwm:
    def __init__(self, ID):
        self.ID = ID
        self.ID_str = '{:02x}'.format(ID)

    def servo_control(self, angle, speed):
        cmd_servo_data = bytes.fromhex('77 68 06 00 02 0B') + bytes.fromhex(self.ID_str) + speed.to_bytes(1,
                                                                                                          byteorder='big',
                                                                                                          signed=True) + \
                         angle.to_bytes(1, byteorder='big', signed=False) + bytes.fromhex('0A')
        # for i in range(0,2):
        serial.write(cmd_servo_data)
        # time.sleep(0.3)
        pass

## 电灯：
class Light:
    def __init__(self, port):
        self.port = port
        self.port_str = '{:02x}'.format(port)

    def light_control(self, which, red, green, blue):  # 0代表全亮，其他值对应灯珠亮，1~4
        which_str = '{:02x}'.format(which)
        red_str = '{:02x}'.format(red)
        green_str = '{:02x}'.format(green)
        blue_str = '{:02x}'.format(blue)
        cmd_servo_data = bytes.fromhex('77 68 08 00 02 3B {} {} {} {} {} 0A'.format(self.port_str, which_str, red_str \
                                                                                    , green_str, blue_str))
        serial.write(cmd_servo_data)

    def light_off(self):
        cmd_servo_data1 = bytes.fromhex('77 68 08 00 02 3B 02 00 00 00 00 0A')
        cmd_servo_data2 = bytes.fromhex('77 68 08 00 02 3B 03 00 00 00 00 0A')
        cmd_servo_data = cmd_servo_data1 + cmd_servo_data2
        serial.write(cmd_servo_data)

## 旋转发动机：抓手移动-2
class Motor_rotate:
    def __init__(self, id, port):
        self.port = port
        self.id = id
        self.id_str = '{:02x}'.format(id)
        self.port_str = '{:02x}'.format(port)

    def motor_rotate(self, speed):
        cmd_servo_data = bytes.fromhex('77 68 06 00 02 0C') + bytes.fromhex(self.id_str) + bytes.fromhex(
            self.port_str) + \
                         speed.to_bytes(1, byteorder='big', signed=True) + bytes.fromhex('0A')
        serial.write(cmd_servo_data)

## 红外线：
class Infrared_value:
    def __init__(self, port):
        port_str = '{:02x}'.format(port)
        self.cmd_data = bytes.fromhex('77 68 04 00 01 D4 {} 0A'.format(port_str))

    def read(self):
        serial.write(self.cmd_data)
        return_data = serial.read()
        if return_data[2] != 0x04:
            return None
        if return_data[3] == 0x0a:
            return None
        return_data_infrared = return_data[3:7]
        print(return_data_infrared)
        infrared_sensor = struct.unpack('<i', struct.pack('4B', *(return_data_infrared)))[0]
        return infrared_sensor

## 蜂鸣器
class Buzzer:
    def __init__(self):
        self.cmd_data = bytes.fromhex('77 68 06 00 02 3D 03 02 0A')

    def rings(self):
        serial.write(self.cmd_data)

## 磁感器：
class Magneto_sensor:
    def __init__(self, port):
        self.port = port
        port_str = '{:02x}'.format(self.port)
        self.cmd_data = bytes.fromhex('77 68 04 00 01 CF {} 0A'.format(port_str))

    def read(self):
        serial.write(self.cmd_data)
        return_data = serial.read()
        # print("return_data=",return_data[8])
        if len(return_data) < 11 or return_data[7] != 0xCF or return_data[8] != self.port:
            return None
        # print(return_data.hex())
        return_data = return_data[3:7]
        mag_sensor = struct.unpack('<i', struct.pack('4B', *(return_data)))[0]
        # print(ultrasonic_sensor)
        return int(mag_sensor)

## 摄像头
class Camera:
    def __init__(self, src=0, shape=[640, 480]):
        self.src = src
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.stopped = False
        for _ in range(10):  # warm up the camera
            (self.grabbed, self.frame) = self.stream.read()

    def start(self):
        threading.Thread(target=self.update, args=()).start()

    def update(self):
        count = 0
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        time.sleep(0.1)
        self.stream.release()
