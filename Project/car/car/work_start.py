"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-08
 @Version   v1.0
 @Function  完整运行程序
 @Comment   None
"""

import time
from car.config import *
from car.task_func import *
from car.component import *


# 确认"4"按键是否按下，程序是否处于等待状态
def check_stop():
    if stop_button.clicked():
        return True
    return False

### 1.等待模式：IDLE (任务从 1 开始)
def idle_handler(params=None):
    global order_num
    print("-NOTICE: current state is IDLE.")

    driver.stop()
    order_num = 1

    while True:
        if start_button.clicked():
            print(" -NOTICE: program start!")
            break
        driver.stop()

    buzzer.rings()
    time.sleep(0.1)
    return STATE_CRUISE, None


# 按照给定速度沿着道路前进给定的时间
def lane_time(speed, my_time):
    start_time = time.time()
    driver.set_speed(speed)
    while True:
        if check_stop():
            return STATE_IDLE, None
        front_image = front_camera.read()
        error = cruiser.infer_cnn(front_image)
        driver.steer(error)
        timeout = time.time()
        if timeout - start_time > my_time:
            driver.stop()
            break


### 2.巡航模式：CRUISE
def cruise_handler(params=None):
    global order_num
    global sign_list
    global cam_dir
    print("-NOTICE: current state is CRUISE.")

    driver.set_speed(DRIVER_SPEED)
    driver.set_kx(DRIVER_KX)

    # (1)设置侧摄像头角度
    servo_turn.servo_control(task[order_num]['angle'], 50)
    time.sleep(0.1)
    print(" -NOTICE: task {} angle {}".format(order_num, task[order_num]['angle']))
    if task[order_num]['angle'] > 45:
        cam_dir = -1
    else:
        cam_dir = 1

    # (2)开启巡航
    while True:
        # (P.S.)监测到按键停止, 进入IDLE
        if check_stop():
            return STATE_IDLE, None
        
        # A.拍摄照片
        front_image = front_camera.read()

        # B.由转弯角度前进
        angle = cruiser.infer_cnn(front_image)
        driver.steer(angle)

        # C.判断车道有无标志
        res = sign_detector.detect(front_image)
        if len(res) != 0:   #监测测到标志 -> 累积
            print(" -NOTICE: sign detected, ", res)
            for sign in res:
                # D.连续加测到一定次数，认为检测到，进入到任务定位程序
                if sign.index == task[order_num]['sign']:
                    sign_list[sign.index] += 1
                    if sign_list[sign.index] > REC_NUM:
                        print(" -NOTICE: sign confired, ", res)
                        return STATE_LOCATE, order_num
        
        else:   #未检测到标志 -> 清零
            sign_list = [0] * 7


def lane_test():
    while True:
        front_image = front_camera.read()
        angle = cruiser.infer_cnn(front_image)
        print(angle)
        time.sleep(0.5)
            
# 标志位置测试
def sign_detecte_test():
    while True:
        front_image = front_camera.read()
        res_front = sign_detector.detect(front_image)
        if len(res_front) > 0:
            print(res_front)
            time.sleep(0.01)

# 任务位置测试
def task_detecte_test():
    while True:

        side_image = side_camera.read()
        res_side = task_detector.detect(side_image)
        if len(res_side) > 0:
            print(res_side)
            time.sleep(1)

def walk_sign(params):
    is_run = True
    while is_run:
        continue_flag = 0
        front_image = front_camera.read()
        # 计算标签偏移，根据标签前进
        res = sign_detector.detect(front_image)
        if len(res) != 0:
            for sign in res:
                print(sign)
                _x, _y = sign.error_from_center()
                print("from center x is{}, y is {}".format(_x, _y))
                if (sign.box[3] - sign.box[1]) < 160:
                    pass
                    # is_run = False
                if _y > 130:
                    is_run = False
                elif _y < 0:
                    continue_flag = 1
                    continue
                if sign.index == task[params]['sign']:
                    angle = _x / 160
                    driver.steer(angle)
                
        if continue_flag == 1:
            angle = cruiser.infer_cnn(front_image)
            driver.steer(angle)
            
    driver.stop()

def walk_seesaw():
    is_run = True
    start_t = time.time() + 2.3
    while is_run:
        front_image = front_camera.read()
        # 计算标签偏移，根据标签前进
        res = sign_detector.detect(front_image)
        if len(res) != 0:
            for sign in res:
                if sign.index == task[8]['sign']:
                    _x, _y = sign.error_from_center()
                    if _y > 50 and abs(_x) < 20:
                        start_t = time.time()
                    if _y > 200:
                        print("nearly")
                        is_run = False
                    if (sign.box[3] - sign.box[1]) < 150:
                        print("height is low")
                        is_run = False
                    angle = _x / 200
                    driver.steer(angle)
        if time.time() - start_t > 0.5:
            is_run = False
            print("time out")
    driver.stop()

# 寻找任务目标
def task_lookfor(params = None):
    time_lookfor = 3
    start_time = time.time()
    find_flag = False
    while find_flag is not True:
        if check_stop():
            return STATE_IDLE, None
        side_image = side_camera.read()
        res_side = task_detector.detect(side_image)
        if len(res_side) > 0:
            print(res_side)
            for res in res_side:
                if res.index in task[params]['index']:
                    # 标签到一定位置退出循环  
                    _x, _y = res.error_from_point(task_functions[res.index]['position'])
                    _x = _x * cam_dir
                    print("find task, distance is:", _x)
                    if task_functions[res.index]['location'] == False:
                        # 不需要定位直接做任务
                        print("do not location ")
                        return res.index
                    else:
                        driver.run(10,10)
                        
                    if _x > POSITION_THRESHOLD:
                        driver.run(-10, -10)
                        return res.index
                    elif _x > 0-POSITION_THRESHOLD:
                        return res.index
        else:
            front_image = front_camera.read()
            angle = cruiser.infer_cnn(front_image)
            driver.steer(angle)
        current_time = time.time()
        # 长时间未到达位置
        if current_time - start_time > LOCATE_TIME:
            return None 
            
def location_ok(params = None):
    start_time = time.time()
    location_flag = False
    while location_flag is not True:
        if check_stop():
            return STATE_IDLE, None
        side_image = side_camera.read()
        res_side = task_detector.detect(side_image)
        if len(res_side) > 0:
            for res in res_side:
                if res.index in task[params]['index']:
                    # 标签到一定位置退出循环
                    _x, _y = res.error_from_point(task_functions[res.index]['position'])
                    _x = _x * cam_dir
                    print(_x)
                    if _x < 0-POSITION_THRESHOLD:
                        print("front")
                        driver.run(10, 10)
                    elif _x > POSITION_THRESHOLD:
                        print("back")
                        driver.run(-10, -10)
                    else:
                        driver.stop()
                        print("location ok")
                        return STATE_DOTASK, res.index
        current_time = time.time()
        # 长时间未到达位置
        if current_time - start_time > 3:
            return STATE_CRUISE, None
        
def adjust_angle():
    while True:
        frame = front_camera.read()
        angle = cruiser.infer_cnn(frame)
        print(angle)
        if angle < -0.01:
            driver.run(0, 15)
        elif angle > 0.01:
            driver.run(15, 0)
        else:
            driver.stop()
            return


### 3.定位模式
def locate_task_handler(params=None):
    global order_num
    global cam_dir
    print("-NOTICE: current state is LOCATE.")

    if params is not None:
        print(" -NOTICE: params is ", params)

        # ????
        walk_sign(params)

        # 8号任务翻山越岭
        if params == 8:
            order_num += 1
            print(" -NOTICE: ready to do task ", params)
            return STATE_DOTASK, task[params]['index'][0]

        # ????
        adjust_angle()

        # 5号任务停车入库
        if task[params]['check'] is not True:
            order_num += 1
            print(" -NOTICE: ready to do task ", params)
            return STATE_DOTASK, task[params]['index'][0]
        
        
        print(" -NOTICE: sign location is ok now.")        
        order_num += 1

        # 调整速度
        if task[params]['location']:
            driver.set_speed(15)
            print(" -NOTICE: current speed is 15")
        else:
            driver.set_speed(20)
            print(" -NOTICE: current speed is 20")
        driver.steer(0)        
            
        if order_num > 11:
            order_num = 11

        # 确认要完成任务号
        print(" -NOTICE: looking for task")
        index = task_lookfor(params)
        print(" -NOTICE: find task ", index)

        if task_functions[index]['location'] == False:
            return STATE_DOTASK, index
        location_ok(params)
        return STATE_DOTASK, index

    else:
        print(" -ERROR: no params, back to cruise.")
        return STATE_CRUISE, order_num


### 4.任务模式
def do_task_handler(params=None):
    print("-NOTICE: current state is DOTASK.")

    print(" -NOTICE: now do task:", str(params), task_functions[params])

    if params == 1:  # alamutu
        driver.stop()
        raise_flag("alamutu")

    elif params == 2:  # bad_person1
        driver.stop()
        shot_target()

    elif params == 3:  # bad_person2
        driver.stop()
        shot_target2()

    elif params == 4:  # dunhuang
        driver.stop()
        raise_flag("dunhuang")

    elif params == 5:  # friendship
        driver.run(0, 22)
        time.sleep(1.2)
        driver.run(23, 23)
        time.sleep(1.7)
        driver.run(15, -15)
        time.sleep(1.35)
        driver.stop()
        
        time.sleep(0.5)
        friendship()
        time.sleep(0.5)
        
        driver.run(15, -15)
        time.sleep(1.2)
        driver.run(23, 23)
        time.sleep(1.6)
        driver.run(0, 22)
        time.sleep(1.2)
        driver.stop()
        
    elif params == 6:  # goodperson1
        lane_time(30,1.5)

    elif params == 7:  # goodperson2
        lane_time(30,1.5)

    elif params == 8:  # jstdb
        driver.stop()
        raise_flag("jstdb")

    elif params == 9:  # purchase
        driver.stop()
        purchase_good()

    elif params == 10:  # trade
        driver.run(-13, -13)
        time.sleep(1.8)
        driver.stop()
        trade_good()

        driver.run(13, 13)
        time.sleep(1.8)
        driver.stop()
        trade_good_1()
        
        driver.run(13, 13)
        time.sleep(1.2)
        driver.stop()
        trade_good_over()   

    elif params == 11:  # seesaw
        lane_time(30,2)

    return STATE_CRUISE, None
