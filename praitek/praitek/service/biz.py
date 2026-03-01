# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import queue
from typing import Optional

import praitek.app
from praitek.app import log
from praitek.service.fr import FaceRecognitionService
from praitek.service.ivatask import IvaTask, IvaEngine
from praitek.service.od import ObjectDetectionService
from praitek.service.rule import EventRuleService
from praitek.service.stream import StreamService

"""
CAP --> OD --> FR --> RULE
        |
        +  --> RULE
"""

# OD线程指 YOLOv8线程，负责Object Detection目标检测
__od_service: Optional[ObjectDetectionService] = None

# 备注：queue.Queue是线程安全的，使用时不需要加锁。
__od_task_q = queue.Queue(maxsize=1000)  # OD线程的输入

# FR线程指 sklearn线程，负责Face Recognition人脸识别
__fr_service: Optional[FaceRecognitionService] = None

# 备注：queue.Queue是线程安全的，使用时不需要加锁。
__fr_task_q = queue.Queue(maxsize=1000)  # FR线程的输入

# RULE 线程，负责比对IVA的检测结果与用户定义的EventRule
__rule_service: Optional[EventRuleService] = None

# 备注：queue.Queue是线程安全的，使用时不需要加锁。
__rule_task_q = queue.Queue(maxsize=1000)


def dispatch_cap_task(task: IvaTask):
    """分发CAPTURE模块返回的任务"""
    tasks = task.split([[IvaEngine.ENG_OD], [IvaEngine.ENG_FR]])

    for subtask in tasks:
        if IvaEngine.ENG_OD in subtask.engines:
            try:
                __od_task_q.put(task, block=False)
            except queue.Full:
                log.warn('od task queue is full')
                # todo 记录系统警告日志
        elif IvaEngine.ENG_FR in subtask.engines:
            try:
                __fr_task_q.put(task, block=False)
            except queue.Full:
                log.warn('fr task queue is full')
                # todo 记录系统警告日志


def dispatch_od_task(task: IvaTask):
    """分发OD模块返回的任务"""
    try:
        __rule_task_q.put(task, block=False)
    except queue.Full:
        log.warn('rule task queue is full')
        # todo 记录系统警告日志


def dispatch_fr_task(task: IvaTask):
    """分发FR模块返回的任务"""
    try:
        __rule_task_q.put(task, block=False)
    except queue.Full:
        log.warn('rule task queue is full')
        # todo 记录系统警告日志


def init_service_env():
    img_path = praitek.app.get_app_conf_value('IMAGE_FOLDER', None, None)
    if img_path is None:
        raise ValueError("IMAGE_FOLDER is not set")

    # 如果imgPath不存在，创建目录
    if not os.path.exists(img_path):
        os.makedirs(img_path)


def create_service():
    init_service_env()

    global __od_service
    __od_service = ObjectDetectionService(__od_task_q, callback=dispatch_od_task)
    __od_service.start()

    global __fr_service
    __fr_service = FaceRecognitionService(__fr_task_q, callback=dispatch_fr_task)
    __fr_service.start()

    global __rule_service
    __rule_service = EventRuleService(__rule_task_q)
    __rule_service.start()

    capture_frequency: float = praitek.app.get_app_conf_value(key='FREQUENCY', section='CAP', default=1)
    if capture_frequency <= 0:
        log.fatal('capture frequency must be greater than 0')
        raise ValueError("capture frequency must be greater than 0")
    else:
        capture_interval = 1 / capture_frequency
    StreamService.instance().start_capture_service(callback=dispatch_cap_task, interval=capture_interval)
    log.info('praitek kernel is started')


def stop_service(signum, frame):
    StreamService.instance().stop_capture_service()
    if __od_service is not None:
        __od_service.stop()
    if __fr_service is not None:
        __fr_service.stop()
    if __rule_service is not None:
        __rule_service.stop()

    __od_service.join()
    __fr_service.join()
    __rule_service.join()

    raise KeyboardInterrupt
