# !/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from praitek.app import app, db
from praitek.infra.stream_engine_map import StreamEngineMap


@dataclass
class Engine(db.Model):
    __tablename__ = 'engine'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String)

    def get_engines_list(self):
        return self.query.order_by(Engine.id).all()

    @staticmethod
    def get_engines_by_stream_id(stream_id: int):
        with app.app_context():
            return db.session.query(Engine).join(StreamEngineMap, Engine.id == StreamEngineMap.engine_id).filter(
                stream_id == StreamEngineMap.stream_id).all()

    @staticmethod
    def get_engines_by_stream_ids(stream_ids: list[int]):
        return (db.session.query(StreamEngineMap.stream_id, Engine.id, Engine.name).
                join(StreamEngineMap, Engine.id == StreamEngineMap.engine_id).
                filter(StreamEngineMap.stream_id.in_(stream_ids)).all())
