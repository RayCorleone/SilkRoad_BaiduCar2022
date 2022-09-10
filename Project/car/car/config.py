"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-08
 @Version   v1.0
 @Function  参数定义
 @Comment   None
"""

### @训练数据收集参数
TRAIN_KX 	= 0.85	#(巡航数据收集)转弯系数
TRAIN_SPEED = 20	#(巡航数据收集)行车速度


### @运动参数
DRIVER_KX 		= 0.85	#运行转弯系数(斜率)
DRIVER_SPEED 	= 30	#车辆运行速度

POSITION_THRESHOLD = 10	#位置偏差阈值
HIGH_SPEED = 40         #高速速度
FULL_SPEED = 30         #中速速度
SLOW_SPEED = 16         #慢速速度，加速速度
ACCELERATION_TIME = 3   #启动时间
SIGN_LOCATE_TIME = 1.4
LOCATE_TIME = 100

### @识别参数
REC_NUM = 3			# 图标出现次数而统计确认识别结果
MISSION_NUM = 11	# 总任务数


### 硬件参数
CONTROLLER 	= "mc601"	# 版号
SIDE_CAM 	= 1   # 边摄像头编号
FRONT_CAM 	= 0   # 前摄像头编号


### 状态参数
STATE_IDLE 		= "idle"
STATE_CRUISE 	= "cruise"
STATE_LOCATE 	= "sign_detected"
STATE_DOTASK 	= "task"


### 标签参数
task = {	#index关联task_functions
	1:{"label":"采购货物", "angle":-50, "check":True, "location":True, "sign":4, "index":[9]},
	2:{"label":"文化交流", "angle":125, "check":True, "location":False, "sign":1, "index":[1, 4, 8]},
	3:{"label":"守护丝路", "angle":125, "check":True, "location":False, "sign":3, "index":[2, 3, 6, 7]},
	4:{"label":"守护丝路", "angle":125, "check":True, "location":False, "sign":3, "index":[2, 3, 6, 7]},
	5:{"label":"放歌友谊", "angle":125, "check":False, "location":False, "sign":2, "index":[5]},
	6:{"label":"守护丝路", "angle":125, "check":True, "location":False, "sign":3, "index":[2, 3, 6, 7],},
	7:{"label":"文化交流", "angle":125, "check":True, "location":False, "sign":1, "index":[1, 4, 8], },
	8:{"label":"翻山越岭", "angle":125, "check":False, "location":False, "sign":5,"index":[11],},
	9:{"label":"文化交流", "angle":125, "check":True, "location":False, "sign":1, "index":[1, 4, 8],},
	10:{"label":"以物易物", "angle":-50, "check":True, "location":False, "sign":6, "index":[10]},
	11:{"label":"守护丝路", "angle":-50, "check":True, "location":False, "sign":3,"index":[2, 3, 6, 7]},
}
        
task_functions = {
	1:{"label":"alamutu","location":False, "position":[155,340]}, # 位置7 阿拉木图
	2:{"label":"badperson1","location":True, "position":[55, 158]}, # 位置10 坏人1
	3:{"label":"badperson2","location":True, "position":[580, 158]}, # 位置3 坏人2
	4:{"label":"dunhuang","location":False, "position":[480,340]},  # 位置2 敦煌
	5:{"label":"friendship","location":False, "position":[]},   #位置5 放歌友谊
	6:{"label":"goodperson1","location":False, "position":[600, 250]},    # 位置4 好人1
	7:{"label":"goodperson2","location":False, "position":[615, 250]},    # 位置6 好人2
	8:{"label":"jstdb","location":False, "position":[480, 340]},  # 位置8 君士坦丁堡
	9:{"label":"purchase","location":True, "position":[240,340]},    # 位置1  采购货物
	10:{"label":"trade","location":True, "position":[230,100]},  # 位置9  以货易货
	11:{"label":"seesaw","location":False, "position":[]},  # 位置9 翻山越岭
}

sign_label = {
	"background": 1, 
	"castle": 1, 
	"friendship": 1, 
	"guard": 1, 
	"purchase": 1, 
	"seesaw":1, 
	"trade": 1
}
