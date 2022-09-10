"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-09
 @Version   v0.0
 @Function  做任务函数
 @Comment   None
"""

import time

from car.component import *


def task_init():
    print("task init ...")
    servo_shot.servo_control(170, 80)   # 收回
    servo_grasp.servo_control(180, 70)  # 关闭抓手
    task_lowest()
    time.sleep(0.5)
    
def task_init_reverse():
    print("task init ...")
    servo_shot.servo_control(160, 80)   # 收回
    servo_grasp.servo_control(180, 70)  # 关闭抓手
    while limit_switch.clicked() is not True:
        motor_UD.motor_rotate(100)
    time.sleep(0.05)
    motor_UD.motor_rotate(0)
    time.sleep(0.5)
    
def task_lowest():
    while limit_switch.clicked() is not True:
        motor_UD.motor_rotate(-100)
    time.sleep(0.05)
    motor_UD.motor_rotate(0)

def task_baseline():
    while limit_switch.clicked() is not True:
        motor_UD.motor_rotate(-100)
    time.sleep(0.05)
    motor_UD.motor_rotate(0)
    
    motor_UD.motor_rotate(100)
    time.sleep(1)
    motor_UD.motor_rotate(0)


def task_down():
    # while True:
    #     kl = magsens.read()
    #     if kl != None and kl >= 70:
    #         break
    #     motor_UD.motor_rotate(-100)
    motor_UD.motor_rotate(-100)
    time.sleep(0.05)
    motor_UD.motor_rotate(0)
    
def task_up():
    print("up ...")
    # while True:
    #     kl = magsens.read()
    #     if kl != None and kl >= 70:
    #         break
    #     motor_UD.motor_rotate(100)
    motor_UD.motor_rotate(100)
    time.sleep(0.05)
    motor_UD.motor_rotate(0)
    print("up ok!")

def light_work(color, tim_t):
    red = [80, 0, 0]
    green = [0, 80, 0]
    yellow = [80, 80, 0]
    off = [0, 0, 0]
    light_color = [0, 0, 0]
    if color == 'red':
        light_color = red
    elif color == 'green':
        light_color = green
    elif color == 'yellow':
        light_color = yellow
    light.light_control(0, light_color[0], light_color[1], light_color[2])
    time.sleep(tim_t)
    light.light_off()

def move_LR(speed_m, time_m):
    motor_LR.motor_rotate(speed_m)
    time.sleep(time_m)
    motor_LR.motor_rotate(0)
    
def move_UD(speed_m, time_m):
    motor_UD.motor_rotate(speed_m)
    time.sleep(time_m)
    motor_UD.motor_rotate(0)
    
def purchase_good():
    task_up()   # 上升到磁感应
    servo_grasp.servo_control(100, 90)   # 打开抓手
    time.sleep(0.4)
    move_LR(-60, 1.4)   # 放出
    servo_grasp.servo_control(180, 70)  # 抓住
    time.sleep(1)
    move_UD(90,1.8) # 上升一些
    move_LR(80, 1.8)  # 收回
    time.sleep(0.5)
    task_lowest()   # 购物完成后下降

def raise_flag(flagname):
    print("raise_flag", flagname,  "start!")
    if flagname == "dunhuang":
        # dunhuang
        servo_raise.servo_control(-40, 60)
        time.sleep(1)
        for i in range(0, 3):
            light_work("green", 0.1)
    elif flagname == "jstdb":
        # jstdb
        servo_raise.servo_control(-120, 60)
        time.sleep(1)
        for i in range(0, 3):
            light_work("green", 0.1)
    elif flagname == "alamutu":
        # almutu
        servo_raise.servo_control(122, 60)
        time.sleep(1)
        for i in range(0, 3):
            light_work("green", 0.1)

    servo_raise.servo_control(42, 60)
    # time.sleep(2)
    print("raise_flag stop!")

def friendship():
    print("friendship start!")
    for i in range(3):
        # print(i)
        light_work("red", 0.2)
        buzzer.rings()
        time.sleep(0.4)
    
def shot_target():
    print("shot_target1 start!")
    task_up() # 上升到磁感应
    move_LR(-50, 0.55)
    move_UD(100, 2)
    time.sleep(0.2)
    servo_shot.servo_control(30, 80)    # 击打
    time.sleep(1.5)
    servo_shot.servo_control(170, 80)   # 收回
    time.sleep(0.5)
    task_down()
    move_LR(50, 1)
    task_lowest()
    motor_UD.motor_rotate(0)
    print("shot_target stop!")

def shot_target2():
    print("shot_target2 start!")
    task_up() # 上升到磁感应
    move_UD(100, 0.5)
    time.sleep(0.2)
    servo_shot.servo_control(30, 80)    # 击打
    time.sleep(1.5)
    servo_shot.servo_control(170, 80)   # 收回
    time.sleep(0.5)
    task_lowest()
    motor_UD.motor_rotate(0)
    print("shot_target stop!")

def trade_good_1():
    print("trade_good_1 start!")
    # 以货易货1层
    move_UD(100, 1)
    move_LR(-50, 0.8) # 伸出抓手
    servo_grasp.servo_control(180, 70) # 闭合抓手
    time.sleep(1.0)
    move_UD(100, 0.8)
    move_LR(50, 2.3) # 收回抓手

def trade_good_2():
    print("trade_good_2 start!")
    # 以货易货2层
    task_up()
    move_LR(-50, 0.5) # 稍微伸出抓手
    move_UD(100, 1)
    task_up()
    move_LR(-50, 1.5) # 伸出抓手
    servo_grasp.servo_control(180, 70) # 闭合抓手
    time.sleep(1.0)
    move_UD(100, 0.8)
    move_LR(50, 1.5) # 收回抓手


def trade_good_over():
    task_lowest()
    move_UD(100, 1)
    move_LR(50,1.5)
    task_lowest()
    
    
def trade_good():
    # 以货易货即将开始
    move_UD(100, 1)
    move_LR(-50, 1.5) # 稍伸抓手
    servo_grasp.servo_control(70, 90)# 张开抓手
    time.sleep(1.0)
    move_LR(50, 2.3) # 收回抓手
    time.sleep(0.8)
    servo_grasp.servo_control(50, 90)    # 张开抓手
    time.sleep(1.0)
