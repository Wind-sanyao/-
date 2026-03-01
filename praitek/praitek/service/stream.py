#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import threading
import time
from datetime import datetime
from typing import Callable, Optional

from praitek.app import log
from praitek.domain.engine import Engine as Engine_domain
from praitek.domain.rule import Rule
from praitek.domain.stream import Stream as Stream_domain, StreamInfoWithEngine, StreamInfo
from praitek.domain.stream import VideoCapturer
from praitek.service.ivatask import IvaTask, IvaEngine


class StreamService:
    __capturer_dict: dict[int, VideoCapturer] = {}
    __capturer_dict_lock = threading.Lock()
    __capture_thread: Optional[threading.Thread] = None
    __capture_stop_flag: bool = False  # 线程的停止标志
    __instance: 'StreamService' = None

    def __init__(self):
        # 启动video captures
        for stream_info in Stream_domain.get_stream_list():
            if stream_info.disabled:
                continue
            capturer = VideoCapturer(stream_info)
            if capturer.start():
                self.__capturer_dict[stream_info.id] = capturer
            else:
                log.warn(f"stream {stream_info.name} is failed to start")
        log.debug(f'totally started {len(self.__capturer_dict)} stream captures.')

    def __del__(self):
        # todo 依次停止可能会很慢，考虑优化方式。
        with self.__capturer_dict_lock:
            for capturer in self.__capturer_dict.values():
                capturer.stop()
            self.__capturer_dict.clear()

    @staticmethod
    def instance() -> 'StreamService':
        if not StreamService.__instance:
            StreamService.__instance = StreamService()
        return StreamService.__instance

    def start_capture_service(self,
                              callback: Callable[[IvaTask], None],
                              interval: float) -> None:
        """
        启动捕获服务

        :param callback: 回调函数，用于处理捕获到的数据。回调函数的参数是 stream id 与 frame
        :param interval: 捕获间隔时间，默认为5.0秒
        :return: None
        """
        self.__capture_stop_flag = False
        self.__capture_thread = threading.Thread(target=self.capture_service_thread, args=(callback, interval))
        self.__capture_thread.start()

    def stop_capture_service(self) -> None:
        """
        停止捕获服务

        :return: None
        """
        self.__capture_stop_flag = True
        if self.__capture_thread is not None:
            self.__capture_thread.join()

    def capture_service_thread(self, callback: Callable[[IvaTask], None], interval: float):
        """
        服务线程，用于捕获相机图像并调用回调函数处理

        :param callback: 回调函数，用于处理捕获的图像
        :param interval: 捕获间隔时间，单位为秒
        :return: None
        """
        while self.__capture_stop_flag is False:
            start_time = datetime.now()  # 获取此循环的开始时间
            with self.__capturer_dict_lock:  # 获取所有capturer的索引
                keys = self.__capturer_dict.keys()

            for key in keys:  # 遍历所有capturer
                try:
                    with self.__capturer_dict_lock:  # 根据索引取得capturer，如果它还存在的话
                        if key in self.__capturer_dict:
                            capture = self.__capturer_dict[key]
                    if capture is None:  # 如果根据索引找不到对应的capturer，则跳过
                        continue
                    frame = capture.snapshot()  # 捕获图像
                    if frame is not None:
                        # 获得frame中的信息
                        # frame_height, frame_width = frame.shape[:2]
                        # print(f"{frame_width}x{frame_height}")
                        # 构建IvaTask
                        stream_info = capture.get_stream_info()
                        task = IvaTask(frame=frame, stream_info=stream_info)
                        task.engines = [IvaEngine(i.id) for i in Engine_domain.get_engine_by_stream_id(stream_info.id)]
                        task.rules = Rule.get_rules_by_stream_and_engine(stream_id=stream_info.id,
                                                                         engine_ids=[int(e.value) for e in
                                                                                     task.engines],
                                                                         hide_disabled=True)
                        # 调用回调函数
                        callback(task)
                except Exception as e:
                    log.error(f"error: stream #{key} capture failed: {e}")

            end_time = datetime.now()
            sleep_time = interval - (end_time - start_time).total_seconds()
            while sleep_time > 0 and self.__capture_stop_flag is False:
                time.sleep(0.1)
                sleep_time -= 0.1

        with self.__capturer_dict_lock:
            keys = self.__capturer_dict.keys()
        for key in keys:
            with self.__capturer_dict_lock:
                if key in self.__capturer_dict:
                    capture = self.__capturer_dict[key]
            capture.stop()
        log.info(f"StreamService stopped gracefully")

    @staticmethod
    def get_stream_info(sid):
        return Stream_domain().get_stream_info(sid).__dict__

    @staticmethod
    def get_stream_list():
        streams = Stream_domain().get_stream_list()
        ids = [stream.id for stream in streams]
        se_map = Engine_domain().get_engines_by_stream_ids(ids)
        return [{
            'id': stream.id,
            'name': stream.name,
            'source_type': stream.source_type,
            'source_url': stream.source_url,
            'account_id': stream.account_id,
            'disabled': stream.disabled,
            'engine_list': se_map[stream.id] if stream.id in se_map.keys() else [],
        } for stream in streams]

    def add_stream(self, stream_info: StreamInfoWithEngine) -> int:
        stream_id = Stream_domain().add_stream(stream_info)
        if stream_info.disabled == 0:
            with self.__capturer_dict_lock:
                if stream_id in self.__capturer_dict.keys():
                    return stream_id

                capturer = VideoCapturer(
                    StreamInfo(stream_id=stream_id, name=stream_info.name, stream_type=stream_info.source_type,
                               stream_url=stream_info.source_url, owner_account_id=stream_info.account_id,
                               disabled=stream_info.disabled))
                self.__capturer_dict[stream_id] = capturer

            if not capturer.start():
                with self.__capturer_dict_lock:
                    self.__capturer_dict.pop(stream_id, None)
                    return -1
        return stream_id

    def update_stream(self, stream_id: int, info: StreamInfoWithEngine, account_id):
        Stream_domain().update_stream(stream_id, info)
        si = Stream_domain().get_stream_info(stream_id)
        with self.__capturer_dict_lock:
            capturer = self.__capturer_dict.pop(stream_id, None)
        if capturer is not None:
            capturer.stop()

        if si.disabled == 0:
            # start stream
            stream_info = StreamInfo(
                stream_id=stream_id, name=si.name, stream_type=si.source_type, stream_url=si.source_url,
                owner_account_id=si.account_id, disabled=si.disabled)
            capturer = VideoCapturer(stream_info)
            with self.__capturer_dict_lock:
                self.__capturer_dict[stream_id] = capturer

            if not capturer.start():
                with self.__capturer_dict_lock:
                    self.__capturer_dict.pop(stream_id, None)

    def delete_stream(self, stream_id: int, account_id: int):
        Stream_domain().delete_stream(stream_id)
        with self.__capturer_dict_lock:
            capturer = self.__capturer_dict.pop(stream_id, None)
        if capturer is not None:
            capturer.stop()
        return

    def activate_stream(self, stream_id, account_id):
        sie = StreamInfoWithEngine(stream_id=stream_id, disabled=0)
        Stream_domain().activate_stream(stream_id, sie)
        stream_info = Stream_domain().get_stream_info(stream_id)

        with self.__capturer_dict_lock:
            if stream_id in self.__capturer_dict.keys():
                return
            capturer = VideoCapturer(stream_info)
            self.__capturer_dict[stream_info.id] = capturer

        if not capturer.start():
            with self.__capturer_dict_lock:
                self.__capturer_dict.pop(stream_id, None)
        return

    def deactivate_stream(self, stream_id, account_id):
        sie = StreamInfoWithEngine(stream_id=stream_id, disabled=1)
        Stream_domain().deactivate_stream(stream_id, sie)

        with self.__capturer_dict_lock:
            if stream_id in self.__capturer_dict.keys():
                capturer = self.__capturer_dict[stream_id]
                self.__capturer_dict.pop(stream_id, None)
        capturer.stop()
        return

    @staticmethod
    def get_snapshot(source_type, source_url):
        si = StreamInfo(stream_id=0, name='test', stream_type=source_type, stream_url=source_url, owner_account_id=0,
                        disabled=0)
        return VideoCapturer.get_snapshot_frame(si)
