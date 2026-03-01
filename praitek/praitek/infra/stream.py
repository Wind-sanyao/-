#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from praitek.app import db
from dataclasses import dataclass

from praitek.infra.stream_engine_map import StreamEngineMap


@dataclass
class Stream(db.Model):
    __tablename__ = 'stream'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String, unique=True)
    source_type: str = db.Column('sourcetype', db.String)
    source_url: str = db.Column('sourceurl', db.String)
    account_id: int = db.Column('accountid', db.Integer)
    disabled: int = db.Column(db.Integer, default=0)

    def get_stream_info(self):
        return self.query.filter_by(id=self.id).first()

    def get_stream_list(self, ids=None):
        rs = self.query
        if ids is not None:
            rs = rs.filter(Stream.id.in_(ids))
        return rs.all()

    @staticmethod
    def add_stream(si, se_maps):
        with db.auto_commit_db():
            db.session.add(si)
            db.session.flush()
            for se_map in se_maps:
                se_map.stream_id = si.id
                db.session.add(se_map)
        return si.id

    def update_stream(self, map_data):
        with db.auto_commit_db():
            self.query.filter_by(id=self.id).update(map_data)

    def delete_stream(self):
        with db.auto_commit_db():
            Stream.query.filter_by(id=self.id).delete()
            StreamEngineMap.query.filter_by(stream_id=self.id).delete()

