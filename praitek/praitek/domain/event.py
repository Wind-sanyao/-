# !/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from praitek.infra.event import Event as Event_infra


class EventInfo:
    id: int
    time: datetime
    stream_name: str
    rule_name: str
    engine_id: int
    image: str
    od_data_str: str

    def __init__(self, eid: int, time: datetime, stream_name: str, rule_name: str, engine_id: int, image: str,
                 od_data_str: str):
        self.id = eid
        self.time = time
        self.stream_name = stream_name
        self.rule_name = rule_name
        self.engine_id = engine_id
        self.image = image
        self.od_data_str = od_data_str


class Event(object):
    def __init__(self):
        pass

    @staticmethod
    def insert_event(time: datetime, stream_name: str, rule_name: str, engine_id: int, image: str,
                     od_data_str: str) -> int:
        return Event_infra.insert_event(timestamp=time, stream_name=stream_name, rule_name=rule_name,
                                        engine_id=engine_id, image=image, od_data_str=od_data_str)

    @staticmethod
    def get_event_list(biz_type, filter_str, order_by, page, size):
        rst, cnt = Event_infra().get_event_list(biz_type, filter_str, order_by, page, size)
        return [EventInfo(eid=e.id, time=e.timestamp, stream_name=e.stream_name, rule_name=e.rule_name,
                          engine_id=e.engine_id, image=e.image, od_data_str=e.od_data_str) for e in rst], cnt
