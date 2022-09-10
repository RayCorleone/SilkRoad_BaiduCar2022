"""
 @Author    NumberONE(Team)
 @Python    python3.9
 @Coding    utf-8
 @Modified  2022-08-09
 @Version   v1.0
 @Function  This module defines common interface PaddleLite.
 @Comment   None
"""

import os
import numpy as np

class PaddlePaddlePredictor:
    """ PaddlePaddle interface wrapper """

    def __init__(self):
        import paddle as pd
        import paddle.fluid as fluid
        from paddle.fluid import debugger
        from paddle.fluid import core
        pd.enable_static()
        self.place = fluid.CPUPlace()
        self.exe = fluid.Executor(self.place)

    def load(self, model_dir):
        import paddle as pd
        import paddle.fluid as fluid
        pd.enable_static()
        # model_dir = j["model"]
        # print(colorize('Loading model: {}'.format(model_dir), fg='green'))
        program = None
        feed = None
        fetch = None
        if os.path.exists(model_dir + "/params"):
            [program, feed, fetch] = fluid.io.load_inference_model(
                model_dir, self.exe, model_filename='model', params_filename="params")
        else:
            print("not combined")
            [program, feed, fetch] = fluid.io.load_inference_model(model_dir, self.exe)

        self.program = program
        self.feed = feed
        self.fetch = fetch
        # print(self.program)
        self.inputs = [None] * len(self.feed)

    def set_input(self, data, index):
        self.inputs[index] = data

    def run(self):
        feeds = {}
        for index, _ in enumerate(self.inputs):
            feeds[self.feed[index]] = self.inputs[index]

        self.results = self.exe.run(program=self.program,
                                    feed=feeds, fetch_list=self.fetch, return_numpy=False)
        self.outputs = []
        for res in self.results:
            self.outputs.append(np.array(res))
        return self.results

    def get_output(self, index):
        return self.results[index]


class PaddleLitePredictor:
    """ PaddlePaddle interface wrapper """
    def __init__(self):
        self.predictor = None

    def load(self, model_dir):
        from paddlelite import Place
        from paddlelite import CxxConfig
        from paddlelite import CreatePaddlePredictor
        from paddlelite import TargetType
        from paddlelite import PrecisionType
        from paddlelite import DataLayoutType
        valid_places = (
            Place(TargetType.kFPGA, PrecisionType.kFP16, DataLayoutType.kNHWC),
            Place(TargetType.kHost, PrecisionType.kFloat),
            Place(TargetType.kARM, PrecisionType.kFloat),
        )
        config = CxxConfig()
        if os.path.exists(model_dir + "/params"):
            config.set_model_file(model_dir + "/model")
            config.set_param_file(model_dir + "/params")
        else:
            config.set_model_dir(model_dir)
        config.set_valid_places(valid_places)
        self.predictor = CreatePaddlePredictor(config)

    def set_input(self, data, index):
        input = self.predictor.get_input(index)
        input.resize(data.shape)
        input.set_data(data)

    def run(self):
        self.predictor.run()

    def get_output(self, index):
        return self.predictor.get_output(index)

