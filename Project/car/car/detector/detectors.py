"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-09
 @Version   v0.0
 @Function  图像识别器类
 @Comment   None
"""

import os
import cv2
import json
import numpy as np
import platform
from os.path import dirname, abspath

from car.config import MISSION_NUM
from car.detector.predictor_wrapper import PaddlePaddlePredictor, PaddleLitePredictor

root_path = dirname(abspath(__file__))

ssd_args = {
    "shape": [1, 3, 480, 480],
    "ms": [127.5, 0.007843]
}

cnn_args = {
    "shape": [1, 3, 128, 128],
    "ms": [125.5, 0.00392157]
}


class DetectionResult:
    def __init__(self, index=0, score=0, name="", box=None, shape=None):
        if shape is None:
            shape = [480, 640]
        if box is None:
            box = [0, 0, 0, 0]
        self.index = index
        self.score = score
        self.name = name
        self.box = list(map(int, box))
        self.center_x = int((self.box[0] + self.box[2]) / 2)
        self.center_y = int((self.box[1] + self.box[3]) / 2)
        self.shape = shape

    def __repr__(self):
        self.center_x = int((self.box[0] + self.box[2]) / 2)
        self.center_y = int((self.box[1] + self.box[3]) / 2)
        width = self.box[2] - self.box[0]
        height = self.box[3] - self.box[1]
        return "index:{} name:{} score:{:.4f} center:({},{}), width:{} height:{}".format(self.index, self.name,
                                                                                         self.score, self.center_x,
                                                                                         self.center_y, width, height)

    def error_from_center(self):
        self.center_x = int((self.box[0] + self.box[2]) / 2)
        self.center_y = int((self.box[1] + self.box[3]) / 2)
        error_x = int(self.center_x - self.shape[1] / 2)
        error_y = int(self.center_y - self.shape[0] / 2)
        return error_x, error_y

    def error_from_point(self, point):
        self.center_x = int((self.box[0] + self.box[2]) / 2)
        self.center_y = int((self.box[1] + self.box[3]) / 2)
        error_x = int(self.center_x - point[0])
        error_y = int(self.center_y - point[1])
        return error_x, error_y


class Detector:
    args = ssd_args
    threshold = 0.3
    """ base class for Detector interface"""

    def __init__(self, model_dir):
        if platform.system() == "Windows":
            self.predictor = PaddlePaddlePredictor()
        else:
            self.predictor = PaddleLitePredictor()

        self.threshold, self.label_list = self.load_model(model_dir)

    def load_model(self, model_dir):
        self.predictor.load(model_dir)
        json_path = model_dir + "/model.json"
        with open(json_path) as j_file:
            j_data = json.load(j_file)
        return j_data["threshold"], j_data["label_list"]

    def image_normalization(self, image):
        shape = self.args["shape"]
        img = cv2.resize(image, (shape[3], shape[2]))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img = img.astype(np.float32)
        img -= 127.5
        img *= 0.007843
        if platform.system() == "Windows":
            img = img.transpose((2, 0, 1))  # HWC to CHW
        img = img.reshape(1, 3, shape[3], shape[2])
        return img

    def infer_ssd(self, data):

        self.predictor.set_input(data, 0)
        self.predictor.run()
        out = self.predictor.get_output(0)
        return np.array(out)

    # should be a class method?
    def res_to_detection(self, item, shape):
        detection_object = DetectionResult()
        detection_object.index = int(item[0])
        detection_object.score = item[1]
        detection_object.name = self.label_list[int(item[0])]
        box = item[2:6] * np.array([shape[1], shape[0], shape[1], shape[0]])

        box[0] = max(box[0], 0)
        box[1] = max(box[1], 1)
        box[2] = min(box[2], shape[1])
        box[3] = min(box[3], shape[0])

        detection_object.box = box.astype(dtype=int)
        return detection_object

    def detect(self, image):
        data = self.image_normalization(image)
        out = self.infer_ssd(data)
        # print(out)
        results = []
        if len(out) <= 0:
            return results
        # out = np.array(out)
        # 设置numpy打印的格式
        np.set_printoptions(precision=4, suppress=True)
        try:
            predict_test = np.array([data for data in out if data[1] > self.threshold])
            # print("predict_test=", predict_test)
        except (IndexError):
            return results
        if len(predict_test) <= 0 or predict_test[0][0] < 0:
            return results

        count = 0
        max_indexes = [-1] * MISSION_NUM
        max_scores = [-1] * MISSION_NUM
        for label, score in predict_test[:, 0:2]:  # zip(predict_data, predict_score):
            # print(label, score)
            if score > max_scores[int(label)]:
                max_indexes[int(label)] = count
                max_scores[int(label)] = score
            count += 1
        selected_indexes = [i for i in max_indexes if i != -1]
        task_index = selected_indexes
        res = predict_test[task_index, :]
        for item in res:
            results.append(self.res_to_detection(item, image.shape))

        return results


class TaskDetector(Detector):

    def __init__(self):
        model_task = "model/task_22"
        model_path = os.path.join(root_path, model_task)
        Detector.__init__(self, model_path)


class SignDetector(Detector):

    def __init__(self):
        model_task = "model/sign_22/"
        model_path = os.path.join(root_path, model_task)
        Detector.__init__(self, model_path)


class Cruiser:
    args = cnn_args

    def __init__(self):
        if platform.system() == "Windows":
            self.predictor = PaddlePaddlePredictor()
        else:
            self.predictor = PaddleLitePredictor()
        model_dir = "model/cruise"
        model_path = os.path.join(root_path, model_dir)
        self.predictor.load(model_path)
        hwc_shape = list(self.args["shape"])
        hwc_shape[3], hwc_shape[1] = hwc_shape[1], hwc_shape[3]
        self.buf = np.zeros(hwc_shape).astype('float32')
        self.size = self.args["shape"][2]
        self.means = self.args["ms"]

    # CNN网络的图片预处理
    def image_normalization(self, image):
        image = cv2.resize(image, (self.size, self.size))

        image = image.astype(np.float32)
        if platform.system() == "Windows":
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = image.transpose((2, 0, 1))  # HWC to CHW
        # 转换成BGR
        img = (image - self.means[0]) * self.means[1]
        img = img.reshape([1, 3, 128, 128])

        return img

    # CNN网络预测
    def infer_cnn(self, image):
        data = self.image_normalization(image)
        self.predictor.set_input(data, 0)

        self.predictor.run()
        out = self.predictor.get_output(0)
        # print(type(out))
        return np.array(out)[0][0]

    def cruise(self, image):
        res = self.infer_cnn(image)
        # print(res)
        return res


def detection_img(results, image):
    for res in results:
        box = res.box
        left = box[0]
        top = box[1]
        right = box[2]
        bottom = box[3]
        start_point = (int(left), int(top))
        end_point = (int(right), int(bottom))
        color = (0, 244, 10)
        thickness = 2
        image = cv2.rectangle(image, start_point, end_point, color, thickness)
        font = cv2.FONT_HERSHEY_SIMPLEX
        point = start_point[0], start_point[1] - 10
        image = cv2.putText(image, res.name, point, font, 1, color, thickness, cv2.LINE_8)
    return image


def test_task_detector(display=True):
    td = TaskDetector()
    test_dir = "image/task"
    result_dir = "image/task_result"
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    assert os.path.exists(result_dir), "不存在%s目录" % result_dir
    print("********************************")
    for root, dirs, files in os.walk(test_dir):
        print(root, dirs, files)
        for file in files:
            file_path = os.path.join(root, file)
            result_path = os.path.join(result_dir, file)
            image = cv2.imread(file_path)
            res = td.detect(image)
            print(res)
            if len(res) > 0:
                image = detection_img(res, image)
                cv2.imwrite(result_path, image)
            show_test(file, image, display)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")


def test_sign_detector(display=True):
    sd = SignDetector()
    test_dir = "image/sign"
    result_dir = "image/sign_result"
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    assert os.path.exists(result_dir), "不存在%s目录" % result_dir
    print("********************************")
    for root, dirs, files in os.walk(test_dir):
        print(root, dirs, files)
        for file in files:
            file_path = os.path.join(root, file)
            result_path = os.path.join(result_dir, file)
            image = cv2.imread(file_path)
            res = sd.detect(image)
            print(res)
            if len(res) > 0:
                image = detection_img(res, image)
                cv2.imwrite(result_path, image)
            show_test(file, image, display)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")


def test_cruise(display=True):
    cruiser = Cruiser()
    test_dir = "image/cruise"
    result_dir = "image/cruise_result"
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    assert os.path.exists(result_dir), "不存在%s目录" % result_dir
    print("********************************")
    for root, dirs, files in os.walk(test_dir):
        print(root, dirs, files)
        for file in files:
            file_path = os.path.join(root, file)
            result_path = os.path.join(result_dir, file)
            frame = cv2.imread(file_path)
            res = cruiser.cruise(frame)
            point = int(frame.shape[1] / 2 - 100), int(frame.shape[0] / 2)
            image = cv2.putText(frame, str(res), point, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_8)
            cv2.imwrite(result_path, image)
            show_test(file, image, display)

    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")


def show_test(name, image, display=True):
    if display:
        cv2.namedWindow(name, 1)
        cv2.moveWindow(name, 400, 200)
        cv2.imshow(name, image)
        cv2.waitKey(0)
        cv2.destroyWindow(name)
        cv2.waitKey(20)
    else:
        return True


def camera_task(detector):
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while True:
        _, image = camera.read()
        res = detector.cruise(image)

        print(res)  #巡航结果
        if len(res) > 0:    #标注检测结果(暂时无用)
            image = detection_img(res, image)
        # cv2.imshow("test", image)
        cv2.waitKey(1)
