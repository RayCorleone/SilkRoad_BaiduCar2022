"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-08
 @Version   v1.0
 @Function  无人驾驶车道数据采集
 @Comment   None
"""

import cv2
import threading
import json
import time
import serial
from os.path import dirname, abspath

from car.collect.joystick import *
from car.cart.widgets import Camera
from car.config import CONTROLLER, TRAIN_KX, TRAIN_SPEED
from car.cart.set_power import start_machine

DEBUG    = 0    # 采集程序不要有print函数，会有冲突,nohup运行时DEBUG需要为0
CNT_BASE = 0    # 图像标号起始
root_path = dirname(abspath(__file__))

comma_head_01_motor = bytes.fromhex('77 68 06 00 02 0C 01 01')
comma_head_02_motor = bytes.fromhex('77 68 06 00 02 0C 01 02')
comma_head_03_motor = bytes.fromhex('77 68 06 00 02 0C 01 03')
comma_head_04_motor = bytes.fromhex('77 68 06 00 02 0C 01 04')
comma_head_all_motor = bytes.fromhex('77 68 0c 00 02 7a 01')
comma_trail = bytes.fromhex('0A')

class SmartCar:
    def __init__(self):
        self.speed = TRAIN_SPEED
        self.kx = TRAIN_KX
        portx = "/dev/ttyUSB0"
        if CONTROLLER == "mc601":
            bps = 380400
            self.move = self.move_mc601
        elif CONTROLLER == "wobot":
            bps = 115200
            self.move = self.move_wobot
        else:
            bps = 115200
            self.move = self.move_wobot
        self.serial_t = serial.Serial(portx, int(bps), timeout=0.0005, parity=serial.PARITY_NONE, stopbits=1)
        
    def steer(self, angle):
        speed = int(self.speed)
        delta = angle * self.kx
        left_wheel = speed
        right_wheel = speed
    
        if delta < 0:
            left_wheel = int((1 + delta) * speed)
        elif delta > 0:
            right_wheel = int((1 - delta) * speed)
        if DEBUG == 1:
            print("left_speed:", left_wheel, "  right_speed:", right_wheel)
        self.move([left_wheel, right_wheel, left_wheel, right_wheel])

    def stop(self):
        self.move([0, 0, 0, 0])
        
    def speed_limit(self, speed):
        if speed > 100:
            speed = 100
        elif speed < -100:
            speed = -100
        else:
            speed = speed
        return speed
        
    def move_wobot(self, speeds):
        left_front = -int(speeds[0]);
        right_front = int(speeds[1]);
        left_rear = -int(speeds[2]);
        right_rear = int(speeds[3]);

        left_front=self.speed_limit(left_front)
        right_front = self.speed_limit(right_front)
        left_rear=self.speed_limit(left_rear)
        right_rear = self.speed_limit(right_rear)
        send_data_01_motor = comma_head_01_motor + left_front.to_bytes(1, byteorder='big', signed=True) + comma_trail
        send_data_02_motor = comma_head_02_motor + right_front.to_bytes(1, byteorder='big', signed=True) + comma_trail
        send_data_03_motor = comma_head_03_motor + left_rear.to_bytes(1, byteorder='big', signed=True) + comma_trail
        send_data_04_motor = comma_head_04_motor + right_rear.to_bytes(1, byteorder='big', signed=True) + comma_trail

        self.serial_t.write(send_data_01_motor)
        self.serial_t.write(send_data_02_motor)
        self.serial_t.write(send_data_03_motor)
        self.serial_t.write(send_data_04_motor)
        
    def move_mc601(self, speeds):
        left_front = int(speeds[0])
        right_front = -int(speeds[1])
        left_rear = int(speeds[2])
        right_rear = -int(speeds[3])

        left_front_kl = bytes.fromhex('01') + left_front.to_bytes(1, byteorder='big', signed=True)
        right_front_kl = bytes.fromhex('02') + right_front.to_bytes(1, byteorder='big', signed=True)
        left_rear_kl = bytes.fromhex('03') + left_rear.to_bytes(1, byteorder='big', signed=True)
        right_rear_kl = bytes.fromhex('04') + right_rear.to_bytes(1, byteorder='big', signed=True)
        send_data_all_motor = (comma_head_all_motor + left_front_kl + right_front_kl + left_rear_kl + right_rear_kl
                               + comma_trail)
        self.serial_t.write(send_data_all_motor)
        time.sleep(0.001)
        
    def rings(self):
        self.serial_t.write(bytes.fromhex('77 68 06 00 02 3D 03 02 0A'))


cart = SmartCar()
front_camera = Camera()
front_camera.start()
js = JoyStick()
js.open()

        
def get_mem():
    with open('/proc/meminfo') as fd:
        for line in fd:
            if line.startswith('MemTotal'):
                total = line.split()[1]
                continue
            if line.startswith('MemFree'):
                free = line.split()[1]
                break
    TotalMem = int(total)/1024.0
    FreeMem = int(free)/1024.0
    print( "FreeMem:"+"%.2f" % FreeMem+'M')
    print( "TotalMem:"+"%.2f" % TotalMem+'M')


def joy_thread():
    global angle
    global start_flag
    global end_flag
    global reset_flag
    
    while end_flag is not True:
        _time, value, type_, number = js.read()
        if js.type(type_) == "button":
            if DEBUG==1:
                print("time:{}, type:{}, value:{}, number:{}".format(_time,type_,value, number))
            if number == 6:
                if value == 0:
                    start_flag = 0
                else:
                    start_flag = 1
            elif number == 10 and value == 1:
                end_flag = True
            elif number == 11 and value == 1:
                reset_flag = 1
        '''         
            if number ==4 and value == 1:
                angle = 0
            elif number == 3 and value == 1:
                angle -= 0.2
            elif number == 1 and value == 1:
                angle += 0.2
            angle = 1 if angle > 1 else angle
            angle = -1 if angle < -1 else angle
            print(angle)
        '''        
        if js.type(type_) == "axis" and number == 2:
            if start_flag == 1:
                # print("axis:{} state: {}".format(number, value))
                angle = value * 1.0 / 32767
                if DEBUG==1:
                    print(angle)
               
            
def driver_thread():
    global angle
    global start_flag
    global end_flag

    while end_flag is not True:
        if start_flag == 1:
            cart.steer(angle)
        else:
            cart.stop()
        time.sleep(0.005)


class VideoOut:
    def __init__(self):
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter('2.avi', self.fourcc, 15, (640, 480))
        self.frames = []
        self.task = threading.Thread(target=self.write, args=())
        self.task.start()
        
    def open(self, path):
        self.out = self.out.open(path, self.fourcc, 15, (640, 480))
        
    def start_write(self,frames):
        self.frames = frames
        # self.write()
        self.task = threading.Thread(target=self.write, args=())
        self.task.start()
    
    def write(self):
        for frame, error in self.frames:
           self.out.write(frame)
 
    def close(self):
        self.task.join()
        self.out.release()


class PicCache:
    def __init__(self):
        self.counter = 0
        self.result_dir = os.path.join(root_path, "train")
        self.roads_data = []
        self.road_json = {}
        self.counter = 0
        self.stoped = False
        self.task = threading.Thread(target=self.save_pic_thread, args=())
        
    def reset(self):
        self.counter = 0
        self.roads_data = []
        self.road_json = {}
    
    def start(self):
        self.task.start()
    
    def save_json(self):
        path = "{}/result_{}.json".format(self.result_dir, CNT_BASE)
        with open(path, 'w') as fp:
            json.dump(self.road_json.copy(), fp)
            
    def append(self,road_data):
        self.roads_data.append(road_data)
        if DEBUG == 1:
            print(len(self.roads_data))
            get_mem()
    
    def save_pic_thread(self):
        while self.stoped is not True:
            if len(self.roads_data) > 0:
                frame,error = self.roads_data[0]
                path = "{}/{}.jpg".format(self.result_dir, self.counter + CNT_BASE)
                cv2.imwrite(path, frame)
                if DEBUG == 1:
                    print("save image",self.counter + CNT_BASE,"ok")
                self.road_json[self.counter + CNT_BASE] = error
                self.roads_data.pop(0)
                self.counter += 1
                if self.counter % 100 == 0:
                    self.save_json()
    
    def close(self):
        while len(self.roads_data) > 0:
            pass
        self.stoped = True
        self.save_json()
        
                    
class PicOut:
    def __init__(self):
        self.counter = 0
        self.result_dir = os.path.join(root_path, "train")
        self.map = {}
        self.frames = []
        self.task = threading.Thread(target=self.write, args=())
        self.task.start()
        self.task_num = 0
        self.counter = 0
    
    def reset(self):
        self.counter = 0
        self.map ={}
        self.frames = []
        
    def save_json(self):
        path = "{}/result_{}.json".format(self.result_dir, CNT_BASE)
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)
            
    def start_write(self,frames):
        self.frames = frames
        self.task = threading.Thread(target=self.write, args=())
        self.task.start()
        # self.task.join()


    def save(self,frame,error):
        path = "{}/{}.jpg".format(self.result_dir, self.counter+CNT_BASE)
        cv2.imwrite(path, frame)
        self.map[self.counter+CNT_BASE] = error
        # print("write:"+str(self.counter))
        self.counter += 1
    
    def write(self):
        # count_t = 0
        for frame, error in self.frames:
            path = "{}/{}.jpg".format(self.result_dir, self.counter+CNT_BASE)
            cv2.imwrite(path, frame)
            self.map[self.counter+CNT_BASE] = error
            if DEBUG==1:
                print("write:"+str(self.counter))
            self.counter += 1
            time.sleep(0.05)
 
    def close(self):
        self.task.join()
        path = "{}/result_{}.json".format(self.result_dir, CNT_BASE)
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)

        
def test_front_video():

    video1 = VideoOut()
    pic = PicOut()
    out_array1 = []
    out_array2 = []
    flag = 0
    counter = 0
    while True:
        img = front_camera.read()

        
        # cv2.imshow("Output", frame)
        if flag == 0:
            out_array1.append(img)
        else:
            out_array2.append(img)
            
        if counter % 200 == 0:
            if flag == 0:
                video1.start_write(out_array1)
                flag = 1
                out_array1 = []
            else:
                video1.start_write(out_array2)
                flag = 0
                out_array2 = []
        if counter > 800:
            break
        counter += 1
        if DEBUG==1:
            print("camera: "+ str(counter))
        
        time.sleep(0.08)
    front_camera.stop()
    video1.close()

    
def pic_test():
    pic = PicOut()
    out_array1 = []
    counter = 0
    while True:
        img = front_camera.read()

        out_array1.append(img)
        if counter % 200 == 0:
            pic.start_write(out_array1)
            flag = 1
            out_array1 = []

        if counter > 800:
            break
        counter += 1
        if DEBUG==1:
            print("camera: "+ str(counter))
        
        time.sleep(0.08)
    front_camera.stop()
    pic.close()
    
        
def main_thread():
    global start_flag
    global angle
    global end_flag
    global reset_flag

    reset_flag = 0
    start_flag = 0
    angle = 0
    counter = 0
    end_flag = False
    result_dir = os.path.join(root_path, "train")
    joy = threading.Thread(target=joy_thread, args=())
    cart_thread = threading.Thread(target=driver_thread, args=())
    joy.start()
    cart_thread.start()
    pic = PicOut()

    out_array1 = []
    errors = []
    get_mem()
    while end_flag is not True:
        if reset_flag == 1:
            pic.reset()
            out_array1 = []
            counter = 0
            cart.rings()
            time.sleep(0.2)
            reset_flag = 0
            continue
        if start_flag == 1:
            t1 = time.time()
            img = front_camera.read()
            error = angle
            
            out_array1.append((img,error))
            if counter % 200 == 0:
                # get_mem()
                
                pic.start_write(out_array1)
                out_array1 = []
            '''
            pic.save(img,error)
            '''
            counter += 1
            time.sleep(0.08)
            fps = int(1 / (time.time() - t1))
            if DEBUG==1:
                print(fps)
    get_mem()
    pic.start_write(out_array1)
    time.sleep(0.2)
    joy.join()
    front_camera.stop()
    pic.close()
    get_mem()

    
def test_thread():
    global start_flag
    global angle
    global end_flag
    global reset_flag

    reset_flag = 0
    start_flag = 0
    angle = 0
    counter = 0
    end_flag = False
    result_dir = os.path.join(root_path, "train")
    joy = threading.Thread(target=joy_thread, args=())
    cart_thread = threading.Thread(target=driver_thread, args=())
    joy.start()
    cart_thread.start()
    pic = PicCache()
    pic.start()

    out_array1 = []
    errors = []
    get_mem()
    while end_flag is not True:
        if reset_flag == 1:
            pic.reset()
            counter = 0
            cart.rings()
            time.sleep(0.2)
            reset_flag = 0
            continue
        if start_flag == 1:
            t1 = time.time()
            img = front_camera.read()
            error = angle
            pic.append((img,error))
            counter += 1
            time.sleep(0.08)
            fps = int(1 / (time.time() - t1))
            if DEBUG==1:
                print("fps is :", fps, "counter is:",counter)
    
    get_mem()
    time.sleep(0.2)
    joy.join()
    front_camera.stop()
    pic.close()
    get_mem()


if __name__ == "__main__":
    start_machine()
    cart.rings()
    time.sleep(0.2)
    cart.rings()
    time.sleep(0.2)
    # main_thread()
    test_thread()
    cart.rings()
    time.sleep(0.2)
    cart.rings()
    time.sleep(0.2)
