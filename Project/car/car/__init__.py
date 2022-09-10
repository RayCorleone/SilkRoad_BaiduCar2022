"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-09
 @Version   v0.0
 @Function  项目打包文件
 @Comment   None
"""

import time

from car.config import *
from car.component import *
from car.task_func import *
from car.work_start import *
from car.cart.set_power import start_machine

def init_app():
    start_machine()  # 启动机器(启用省电关闭)

    front_camera.start()
    side_camera.start()

    driver.set_speed(40)
    driver.set_kx(1)

    order_num = 1
    time.sleep(0.1)
    
    task_init()     # 初始化任务(收回抓手 关闭抓手)
    time.sleep(0.2)


def create_app():
    ## 1.初始化程序
    init_app()
    buzzer.rings()  # 蜂鸣器提示已启动

    ## 2.循环执行
    params = None
    cur_state = STATE_IDLE
    while True:
        print("-NOTICE: new round.")

        if cur_state is STATE_IDLE:     # 1.等待处理
            cur_state, params = idle_handler()
        elif cur_state is STATE_CRUISE: # 2.巡航模式
            cur_state, params = cruise_handler(order_num)
        elif cur_state is STATE_LOCATE: # 3.定位模式
            cur_state, params = locate_task_handler(params)
        elif cur_state is STATE_DOTASK: # 4.任务模式
            cur_state, params = do_task_handler(params)
        else:
            print("-ERROR: state ", cur_state, " not defined")
