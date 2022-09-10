"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-08
 @Version   v1.0
 @Function  驾驶摇杆类定义
 @Comment   None
"""

import os
import struct


class JoyStick:
    def __init__(self):
        print('avaliable devices')
        for fn in os.listdir('/dev/input'):
            if fn.startswith('js'):
                print('/dev/input/%s' % fn)

        self.fn = '/dev/input/js0'
        self.x_axis = 0

    def open(self):
        self.jsdev = open(self.fn, 'rb')

    def read(self):
        self.evbuf = self.jsdev.read(8)
        return struct.unpack('IhBB', self.evbuf)

    def type(self, type_):
        if type_ & 0x01:
            return "button"
        if type_ & 0x02:
            return "axis"

    def button_state(self):
        return 1

    def get_x_axis(self):
        time, value, type_, number = struct.unpack('IhBB', self.evbuf)
        if number == 1:
            fvalue = value / 32767
            return fvalue        
