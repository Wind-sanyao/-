# !/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

from praitek.app import db, app


@dataclass
class Event(db.Model):
    __tablename__ = 'event'

    id: int = db.Column("id", db.Integer, primary_key=True)
    timestamp: datetime = db.Column("timestamp", db.DateTime)
    stream_name: str = db.Column("streamname", db.String)
    rule_name: str = db.Column("rulename", db.String)
    engine_id: int = db.Column("engineid", db.Integer)
    image: str = db.Column("image", db.String)
    od_data_str: str = db.Column("oddata", db.String)

    @staticmethod
    def insert_event(timestamp: datetime, stream_name: str, rule_name: str, engine_id: int, image: str,
                     od_data_str: str) -> int:
        with app.app_context():
            evt = Event(timestamp=timestamp, stream_name=stream_name, rule_name=rule_name, engine_id=engine_id,
                        image=image, od_data_str=od_data_str)
            db.session.add(evt)
            db.session.flush()
            db.session.commit()
            return evt.id

    @staticmethod
    def get_event_by_id(id0: int) -> "Event":
        with app.app_context():
            return db.session.query(Event).filter(Event.id == id0).first()

    def get_event_list(self, biz_type: int = 0, filter_str: str = '', order_by: str = '', page: int = 1,
                       size: int = 30):
        rs = self.query
        if biz_type != 0:
            rs = rs.filter_by(engine_id=biz_type)
        if filter_str != '':
            s = '%' + filter_str + '%'
            rs = rs.filter(Event.od_data_str.like(s))
        cnt = rs.count()
        if order_by == 'time':
            rs = rs.order_by(Event.timestamp)
        elif order_by == '-time':
            rs = rs.order_by(Event.timestamp.desc())
        if page > 0 and size > 0:
            return rs.paginate(page=page, per_page=size).items, cnt
        else:
            return rs.all(), cnt

    def get_event_info(self):
        return self.query.filter_by(id=self.id).first()


def test_main():
    # Event.insert_event(1, "test", "test", "test", "test")
    event = Event.get_event_by_id(1)
    print(event.timestamp.timestamp())


if __name__ == '__main__':
    test_main()
