# !/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional

from praitek.app import db, app
from praitek.infra.se_rule_map import StreamEngineRuleMap


@dataclass
class StreamEngineMap(db.Model):
    __tablename__ = 'stream_engine_map'

    id: int = db.Column(db.Integer, primary_key=True)
    stream_id: int = db.Column('streamid', db.Integer)
    engine_id: int = db.Column('engineid', db.Integer)

    def get_map_list(self):
        return self.query.all()

    def add_stream_engine_map(self):
        with db.auto_commit_db():
            db.session.add(self)
            db.session.flush()
            seid = self.id
        return seid

    def delete_stream_engine_map(self):
        with db.auto_commit_db():
            self.query.filter_by(id=self.id).delete()

    @staticmethod
    def get_seid_by_stream_and_engine(stream_id: int, engine_id: int) -> Optional[int]:
        """
        get_id_by_stream_and_engine

        :param stream_id:
        :param engine_id:
        :return: None if no match record
        """
        # Execute database operations within the application context
        with app.app_context():
            rs = db.session.query(StreamEngineMap).filter(StreamEngineMap.stream_id == stream_id).filter(
                StreamEngineMap.engine_id == engine_id).with_entities(StreamEngineMap.id).all()

            # Check if there are any query results
            if len(rs) > 0:
                # If there are results, return the id value of the first record
                return rs[0][0]
            else:
                # If there are no query results, return None
                return None

    def update_stream_engine_map(self, engine_ids):
        old_engine_ids = [i for (i,) in
                          self.query.with_entities(StreamEngineMap.engine_id).filter_by(stream_id=self.stream_id).all()]
        del_engine_ids = set(old_engine_ids).difference(set(engine_ids))
        add_engine_ids = set(engine_ids).difference(set(old_engine_ids))

        sems = [StreamEngineMap(stream_id=self.stream_id, engine_id=eid) for eid in add_engine_ids]
        del_ids = [i for (i,) in db.session.query(StreamEngineMap.id).filter_by(stream_id=self.stream_id).filter(
            StreamEngineMap.engine_id.in_(del_engine_ids)).all()]
        with db.auto_commit_db():
            self.query.filter(StreamEngineMap.id.in_(del_ids)).delete()
            StreamEngineRuleMap.query.filter(StreamEngineRuleMap.se_id.in_(del_ids)).delete()
            db.session.add_all(sems)
        return


def test_main():
    ret = StreamEngineMap.get_seid_by_stream_and_engine(2, 1)
    print(ret, type(ret))


if __name__ == '__main__':
    test_main()
