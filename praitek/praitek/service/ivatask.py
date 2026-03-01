import copy
from datetime import datetime, timezone
from enum import Enum

import cv2
from numpy import ndarray

from praitek.domain.object_detection import Box
from praitek.domain.rule import Rule
from praitek.domain.stream import StreamInfo, Stream


class IvaEngine(Enum):
    """下列数值必须和数据库中的保持一致！"""
    ENG_OD = 1
    ENG_FR = 2


class IvaTask(object):
    """service包内使用的数据结构"""

    # 以下是VideoCapturer填写的字段
    frame: ndarray  # cv2.read()方法读取的图像数据
    stream_info: StreamInfo  # 数据库中关于stream的信息
    datetime: datetime  # Task生成的时间
    engines: list[IvaEngine]  # stream 支持的 engine 列表
    rules: list[Rule]

    # 以下是OD模块填写的字段
    boxes: list[Box]  # 从OD模块得到的box列表

    def __init__(self, frame: ndarray, stream_info: StreamInfo):
        self.frame = frame.copy()
        self.stream_info = copy.copy(stream_info)
        self.datetime = datetime.now(timezone.utc)

    def split(self, groups: list[list[IvaEngine]]) -> list["IvaTask"]:
        """
        解释：一个task中指派了多个引擎，那么在任务执行到某个步骤时，就要将一个task拆分成多个task，分别分配给不同的处理过程。
        重点！！ 拆分后的task对象共享原来task中的数据（指针），只有 engines 列表是各自独立的。

        :param groups: 根据group中的分组进行拆分，拆出来的任一任务中还是可以包含多个引擎。
        :return:
        """
        ret: list[IvaTask] = []
        for group in groups:
            task1 = copy.copy(self)
            task1.engines = list(set(group).intersection(set(self.engines)))
            ret.append(task1)
        return ret


def test_main():
    stream_info = Stream().get_stream_list()[0]
    frame = cv2.imread("7.png")

    task = IvaTask(frame=frame, stream_info=stream_info)
    box = Box(0, 0.98, [100, 100, 200, 200], {0: "face"})
    task.boxes = [box]
    task.engines = [IvaEngine.ENG_OD, IvaEngine.ENG_FR]

    tasks = task.split([[IvaEngine.ENG_OD], [IvaEngine.ENG_FR, IvaEngine.ENG_OD]])
    print(tasks)
    return


if __name__ == '__main__':
    test_main()
