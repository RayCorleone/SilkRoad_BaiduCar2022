import cv2
import time
import sys

sys.path.append("../")
from cart.widgets import Button

# 摄像头编号
# cam=0
cam = 1

start_button = Button(1, "2")   # 程序开启运行开关
stop_button = Button(1, "4")    # 程序关闭开关

camera = cv2.VideoCapture(cam)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
btn = 0

if __name__ == "__main__":
    if cam == 0:
        result_dir = "./front_image"
    else:
        result_dir = "./side_image"

    print("Start!")
    print('''Press the "4 button" to take photos!''')

    while True:
        if stop_button.clicked():
            print("btn", btn)
            path = "{}/{}.png".format(result_dir, btn)
            btn += 1
            time.sleep(0.2)
            return_value, image = camera.read()
            name = "{}.png".format(btn)
            cv2.imwrite(path, image)

