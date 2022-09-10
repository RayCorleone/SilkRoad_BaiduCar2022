"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-09
 @Version   v0.0
 @Function  项目组件和通用变量声明
 @Comment   None
"""

from car.cart.widgets import *
from car.cart.driver import Driver
from car.config import FRONT_CAM, SIDE_CAM
from car.detector.detectors import Cruiser, SignDetector, TaskDetector


## 部分通用常量
cam_dir     = 1         #测摄像头方向(左边为-1，右边为1)
order_num   = 1         #
sign_list   = [0] * 11  #


## 通用汽车组件
front_camera = Camera(FRONT_CAM, [640, 480])    #前摄像头
side_camera  = Camera(SIDE_CAM, [640, 480])     #侧摄像头
start_button = Button_angel(1, "2")     #程序开启运行开关
stop_button  = Button_angel(1, "4")     #程序重置停止开关
light        = Light(6)             #集成灯接D3口(D6口)
buzzer       = Buzzer()             #蜂鸣器
motor_LR     = Motor_rotate(2, 1)   #左右移动电机
motor_UD     = Motor_rotate(2, 2)   #上下移动电机
limit_switch = LimitSwitch(4)       #限位开关
servo_shot   = Servo_pwm(5)         #击打伺服
servo_grasp  = Servo_pwm(1)         #抓手伺服
servo_turn   = Servo(2)             #测摄像头旋转伺服
servo_raise  = Servo(1)             #举旗旋转伺服
magsens      = Magneto_sensor(3)    #磁感应


## 包装功能组件
driver  = Driver()              #汽车驾驶控制
cruiser = Cruiser()             #巡航路线检测
sign_detector = SignDetector()  #地面标志检测
task_detector = TaskDetector()  #侧边目标物检测
