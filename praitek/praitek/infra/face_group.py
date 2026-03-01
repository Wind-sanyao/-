# !/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from praitek.app import db
from praitek.infra.face_group_map import FaceGroupMap


@dataclass
class FaceGroup(db.Model):
    __tablename__ = 'facegroup'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String)

    def get_group_list(self):
        return self.query.all()

    def add_group_info(self):
        with db.auto_commit_db():
            db.session.add(self)
            db.session.flush()
            gid = self.id
        return gid

    def delete_group_info(self):
        with db.auto_commit_db():
            FaceGroup.query.filter_by(id=self.id).delete()
            FaceGroupMap.query.filter_by(group_id=self.id).delete()

    def update_group_info(self, map_data):
        with db.auto_commit_db():
            self.query.filter_by(id=self.id).update(map_data)

    @staticmethod
    def get_group_list_by_face_list(ids):
        return (db.session.query(FaceGroup.id, FaceGroup.name, FaceGroupMap.face_id).
                join(FaceGroupMap, FaceGroup.id == FaceGroupMap.group_id).
                filter(FaceGroupMap.face_id.in_(ids)).all())
