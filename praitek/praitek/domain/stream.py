# !/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import time
from typing import Optional

import cv2
from numpy import ndarray

from praitek.app import log
from praitek.infra.stream import Stream as Stream_infra
from praitek.infra.stream_engine_map import StreamEngineMap as SEmap_infra


class StreamInfo:
    id: int
    name: str
    source_type: str
    source_url: str
    account_id: int
    disabled: int

    def __init__(self, stream_id: int, name: str, stream_type: str, stream_url: str, owner_account_id: int,
                 disabled: int):
        self.id = stream_id
        self.name = name
        self.source_type = stream_type
        self.source_url = stream_url
        self.account_id = owner_account_id
        self.disabled = disabled
        return


class StreamInfoWithEngine:
    id: int
    name: str
    source_type: Optional[str]
    source_url: Optional[str]
    account_id: Optional[int]
    disabled: Optional[int]
    engine_ids: Optional[list[int]]

    def __init__(self, stream_id: int, name: Optional[str] = None, stream_type: Optional[str] = None,
                 stream_url: Optional[str] = None, owner_account_id: Optional[int] = None, disabled: Optional[
                int] = None,
                 engine_ids: Optional[list[int]] = None):
        self.id = stream_id
        self.name = name
        self.source_type = stream_type
        self.source_url = stream_url
        self.account_id = owner_account_id
        self.disabled = disabled
        self.engine_ids = engine_ids
        return


class Stream:
    def __init__(self):
        return

    @staticmethod
    def get_stream_info(stream_id):
        data = Stream_infra(id=stream_id).get_stream_info()
        return StreamInfo(stream_id=data.id, name=data.name, stream_type=data.source_type, stream_url=data.source_url,
                          owner_account_id=data.account_id, disabled=data.disabled)

    @staticmethod
    def get_stream_list(ids=None):
        streams = Stream_infra().get_stream_list(ids)
        datas = [
            StreamInfoWithEngine(stream_id=stream.id, name=stream.name, stream_type=stream.source_type,
                                 stream_url=stream.source_url,
                                 owner_account_id=stream.account_id, disabled=stream.disabled) for stream in streams]
        return datas

    @staticmethod
    def add_stream(sie: StreamInfoWithEngine):
        si = Stream_infra(name=sie.name, source_type=sie.source_type, source_url=sie.source_url,
                          account_id=sie.account_id, disabled=sie.disabled)
        se_maps = [SEmap_infra(engine_id=i) for i in sie.engine_ids]
        return si.add_stream(si, se_maps)

    @staticmethod
    def update_stream(stream_id: int, sie: StreamInfoWithEngine):
        """存入数据库"""
        map_data = {name: value for name, value in vars(sie).items() if
                    value is not None and name not in ['id', 'engine_ids']}
        if map_data != {}:
            Stream_infra(id=stream_id).update_stream(map_data)
        SEmap_infra(stream_id=stream_id).update_stream_engine_map(engine_ids=sie.engine_ids)
        return

    @staticmethod
    def delete_stream(stream_id: int):
        si = Stream_infra(id=stream_id)
        return si.delete_stream()

    @staticmethod
    def deactivate_stream(stream_id: int, sie: StreamInfoWithEngine):
        """存入数据库"""
        map_data = {'disabled': 1}
        Stream_infra(id=stream_id).update_stream(map_data)
        return

    @staticmethod
    def activate_stream(stream_id: int, sie: StreamInfoWithEngine):
        """存入数据库"""
        map_data = {'disabled': 0}
        Stream_infra(id=stream_id).update_stream(map_data)
        return


class VideoCapturer:
    """
    定义：视频捕获器
    功能：使用OpenCV捕获视频的截图。

    使用步骤：
    1. 初始化VideoCapturer对象。
    2. 调用start()方法启动视频获取器线程。
    3. 不定期调用snapshot()方法捕获视频流的截图。
    4. 调用stop()方法停止视频获取器线程。

    补充：对usb和rtsp，捕获器返回最新的一帧。对file，返回下一帧。
    """

    __stop_flag: bool = False  # 停止线程的标志
    __cap: Optional[cv2.VideoCapture] = None
    __thread: Optional[threading.Thread] = None
    __snapshot_flag: bool = False  # 在snapshot()方法中设置，通知线程取出一张截图。
    __snapshot_frame = None  # 保存视频截图
    __snapshot_cond = threading.Condition()  # 用于同步snapshot()和线程的锁，同时也使snapshot()不可重入。

    def __init__(self, stream_info: StreamInfo):
        self.__stream_info: StreamInfo = stream_info  # 记录视频流的基本信息

    def __thread_func(self):
        """
        定义：视频捕获器的线程函数。
        功能：获取视频流并从中截图的线程函数。

        1. 打开视频流。
        2. 如果snapshot_flag为True，保存当前帧到snapshot_frame。
        3. 等待0.01秒。
        4. 如果stop_flag为True，退出。
        """
        try:
            while True:
                if self.__snapshot_flag:
                    # 根据stream的类型使用不同的read()方法
                    if self.__stream_info.source_type == 'rtsp':
                        ret, frame = self.__cap.retrieve()
                    else:
                        ret, frame = self.__cap.read()
                    if not ret:
                        frame = None
                    self.__snapshot_cond.acquire()
                    self.__snapshot_frame = frame
                    self.__snapshot_flag = False
                    self.__snapshot_cond.notify()
                    self.__snapshot_cond.release()
                else:
                    if self.__stream_info.source_type == 'rtsp':
                        self.__cap.grab()
                time.sleep(0.001)

                # 把退出条件判断放在这里，可以防止在调用notify()方法之前退出，导致snapshot()方法阻塞。
                if self.__stop_flag is True:
                    break
                time.sleep(0.01)
        finally:
            self.__cap.release()

    def start(self) -> bool:
        """
        定义：启动视频捕获器

        :return: 是否成功启动
        """

        if self.__stream_info.source_type == 'rtsp':
            self.__cap = cv2.VideoCapture(self.__stream_info.source_url)
        elif self.__stream_info.source_type == 'usb':
            self.__cap = cv2.VideoCapture(int(self.__stream_info.source_url))
        else:
            raise Exception(f'unsupported source type "{self.__stream_info.source_type}"')

        if not self.__cap.isOpened():
            log.error(f'open video capturer on "{self.__stream_info.source_url}" failed')
            return False

        self.__thread = threading.Thread(target=self.__thread_func, name=self.__stream_info.name)
        self.__stop_flag = False
        self.__thread.start()
        return True

    def stop(self):
        """定义：停止视频捕获器"""
        self.__stop_flag = True
        # todo 考虑在这里调用condition.notify()方法，防止snapshot()方法阻塞。
        if self.__thread is not None:
            self.__thread.join()

    def snapshot(self, timeout: float = 1.0) -> Optional[ndarray]:
        """
        定义：从视频流捕获一张截图。
        :return:
        """
        # 检查视频捕获器是否正在运行
        if self.__thread is None or not self.__thread.is_alive():
            log.error('video capturer is not running')
            return None

        self.__snapshot_cond.acquire()
        try:
            if self.__stop_flag is False:
                self.__snapshot_flag = True
                self.__snapshot_cond.wait(timeout)
            return self.__snapshot_frame
        finally:
            self.__snapshot_cond.release()

    def get_stream_info(self) -> StreamInfo:
        return self.__stream_info

    @staticmethod
    def get_snapshot_frame(stream_info):
        capturer = VideoCapturer(stream_info)
        ok = capturer.start()
        if ok:
            for i in range(3):
                frame = capturer.snapshot()
                if frame is not None:
                    data = cv2.imencode('.png', frame)[1]
                    img = data.tobytes()
                    capturer.stop()
                    return img
                time.sleep(0.5)
        raise


def test_main():
    stream_info = StreamInfo(stream_id=1, name='test', stream_type='rtsp',
                             stream_url='rtsp://admin:abc.123456@192.168.250.162/Streaming/Channels/102',
                             owner_account_id=1,
                             disabled=0)
    capturer = VideoCapturer(stream_info)
    ret = capturer.start()
    while ret:
        frame = capturer.snapshot()
        if frame is not None:
            cv2.putText(frame, 'Press Q to quit', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            cv2.imshow('test', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        time.sleep(0.5)
    capturer.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    test_main()
