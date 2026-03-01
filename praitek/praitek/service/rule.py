# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import queue
import threading
import time
from datetime import timedelta

import cv2

import praitek.app
from praitek.app import log
from praitek.domain.action import Action
from praitek.domain.engine import Engine
from praitek.domain.event import Event
from praitek.domain.object_detection import Box
from praitek.domain.rule import Rule
from praitek.domain.stream import Stream
from praitek.infra.event_rule import EventRule as Rule_infra
from praitek.infra.face import Face as Face_infra
from praitek.service.ivatask import IvaTask, IvaEngine


class EventRuleService(threading.Thread):
    """
    事件规则服务

    功能：将IVA分析的结果与用户定义的EventRule做比对，把满足条件的事件发送给用户。
    """
    __stop_flag: bool = False

    def __init__(self, queue_in: queue.Queue):
        super().__init__()
        self.__q_in = queue_in
        self.name = EventRuleService.__name__

    def run(self):
        while not self.__stop_flag:
            try:
                task: IvaTask = self.__q_in.get(timeout=0.5)
                for rule in task.rules:
                    with praitek.app.app.app_context():
                        boxes_matched = EventRuleService.__do_test_on_rule(task.boxes, rule, task.engines[0])
                        if len(boxes_matched) == 0:
                            continue
                        if not Retarder.filtrate(rule, task):
                            continue
                        task.boxes = boxes_matched
                        EventRuleService.__send_event(rule, task)
            except queue.Empty:
                pass
            except Exception as e:
                log.error(e)
            finally:
                time.sleep(0.001)
        log.info("EventRuleService stopped gracefully")

    def stop(self):
        self.__stop_flag = True

    @staticmethod
    def __do_test_on_rule(boxes: list[Box], rule: Rule, engine_id: IvaEngine) -> list[Box]:
        if len(boxes) == 0:
            return []

        if engine_id == IvaEngine.ENG_OD:
            # 如果 boxes 中 class_name 含有 rule.rule_str
            class_name_in_rule = rule.rule_str.lower()
            log.debug(f'searching {class_name_in_rule} in {[b.class_name for b in boxes]}')
            boxes_matched = [box for box in boxes if box.class_name.lower() == class_name_in_rule]
            # for box in boxes:
            #     if box.class_name.lower() == class_name_in_rule:
            #         log.debug(f"found {class_name_in_rule} in {box.class_name}")
            #         boxes_matched.append(box)
            # log.debug(f"not found {class_name_in_rule}")

        elif engine_id == IvaEngine.ENG_FR:
            # split rule.rule_str by "," and convert them to int
            face_group_ids: tuple[int] = tuple[int]((int(i) for i in rule.rule_str.split(",")))
            faces_expected = Face_infra.get_face_list_by_group_ids(face_group_ids)
            faces_expected_dict = {f.id: f.name for f in faces_expected}
            boxes_matched = []
            for box in boxes:
                # fix box: move box.class_name to box.class_id
                try:
                    box.class_id = int(box.class_name)
                except ValueError:
                    pass
                else:
                    if box.class_id in faces_expected_dict.keys():
                        box.class_name = faces_expected_dict[box.class_id]
                        boxes_matched.append(box)
        else:
            return []
        return boxes_matched

    @staticmethod
    def __send_event(rule: Rule, task: IvaTask) -> None:
        img_filename = f"{task.stream_info.id}_{rule.id}_{task.datetime.strftime('%Y%m%d%H%M%S')}"
        full_name = os.path.join(praitek.app.get_app_conf_value("IMAGE_FOLDER", None, None), img_filename + ".png")
        cv2.imwrite(filename=full_name, img=task.frame)  # 保存图像

        # image_d = task.frame.copy()  # 画OD图层
        # for box in task.boxes:
        #     x1y1 = (box.xyxy[0], box.xyxy[1])
        #     x2y2 = (box.xyxy[2], box.xyxy[3])
        #     image_d = cv2.rectangle(image_d, x1y1, x2y2, color=(0, 255, 0), thickness=2)
        # full_name = os.path.join(app.config["IMAGE_FOLDER"], img_filename + "d.png")
        # cv2.imwrite(filename=full_name, img=image_d)  # 保存含OD图层的图像

        rule: Rule_infra = Rule_infra(name=rule.name).get_rule_by_name()
        od_data_str = ";".join([repr(box) for box in task.boxes])  # 所有box信息保存在一个字符串中
        eid = Event.insert_event(task.datetime, stream_name=task.stream_info.name, rule_name=rule.name,
                                 engine_id=int(task.engines[0].value), image=img_filename, od_data_str=od_data_str)

        Action.send_notification(rule_id=rule.id, event_id=eid, stream_name=task.stream_info.name,
                                 event_time=task.datetime)
        return

    @staticmethod
    def get_event_rule_list():
        rules = Rule.get_rule_list()

        stream_ids = [stream.get('id', 0) for rule in rules for stream in rule.streams]
        stream_map = {i.id: i.name for i in Stream.get_stream_list(stream_ids)}
        for rule in rules:
            for s in rule.streams:
                if s['id'] in stream_map.keys():
                    s['name'] = stream_map[s['id']]

        engines = Engine.get_engine_list()
        eng_map = {engine.id: engine.name for engine in engines}

        for rule in rules:
            rule.engine_name = eng_map[rule.engine_id] if rule.engine_id != 0 else ''

        return [rule.__dict__ for rule in rules]

    @staticmethod
    def get_event_rule_info(rule_id):
        rule = Rule.get_event_rule_info(rule_id)

        stream_ids = [stream.get('id', 0) for stream in rule.streams]
        stream_map = {i.id: i.name for i in Stream.get_stream_list(stream_ids)}
        for s in rule.streams:
            if s['id'] in stream_map.keys():
                s['name'] = stream_map[s['id']]

        engines = Engine.get_engine_list()
        eng_map = {engine.id: engine.name for engine in engines}
        rule.engine_name = eng_map[rule.engine_id] if rule.engine_id != 0 else ''

        rule.actions = Action.get_event_action_list_by_rule(rule_id)

        return rule.__dict__

    @staticmethod
    def add_event_rule_info(rule):
        return Rule.add_event_rule_info(rule)

    @staticmethod
    def delete_event_rule_info(rule_id: int) -> None:
        return Rule.delete_event_rule_info(rule_id)

    @staticmethod
    def update_event_rule_info(rule):
        return Rule.update_event_rule_info(rule)


class Retarder:
    history_repo = {}
    lock = threading.Lock()
    __retarder_min_interval = timedelta(
        seconds=praitek.app.get_app_conf_value(key='RETARDER_INTERVAL_MIN', section='EVENT', default=15))

    @staticmethod
    def filtrate(rule: Rule, task: IvaTask) -> bool:
        """
        过滤频繁的事件
        返回True表示可以发送事件，False表示不发送
        """

        # 创建一个主键，用于存放历史记录
        key_of_history = f"{rule.id}_{task.stream_info.id}"

        with Retarder.lock:
            # 从历史中查找
            if key_of_history not in Retarder.history_repo.keys():
                Retarder.update_history(key_of_history, task)
                return True

            history = Retarder.history_repo[key_of_history]

            # delta = task.datetime - history["last_time"]
            # log.debug(f'{task.datetime} --- {history["last_time"]}')
            # log.debug(f'{delta} vs {Retarder.__retarder_min_interval}')
            if task.datetime - history["last_time"] < Retarder.__retarder_min_interval:
                # 如果时间间隔小于设定值，则不发送事件
                # print('限速条件，不发送事件')
                return False

            # print('不满足降速条件，发送事件')
            # 不满足降速条件，发送事件
            Retarder.update_history(key_of_history, task)
            return True

    @staticmethod
    def update_history(key: str, task: IvaTask) -> None:
        """
        将当前帧和事件内容存入历史档案
        """
        Retarder.history_repo[key] = {
            "last_time": task.datetime,
            "last_frame": task.frame,
            "last_boxes": task.boxes,
        }

    @staticmethod
    def clear_ancient_history() -> None:
        """
        清除古老的历史记录
        """
        with Retarder.lock:
            # TODO 择时清理历史记录
            Retarder.history_repo.clear()
