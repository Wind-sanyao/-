# !/usr/bin/env python
# -*- coding: utf-8 -*-
from praitek.app import db
from dataclasses import dataclass


@dataclass
class FaceGroupMap(db.Model):
    __tablename__ = 'face_group_map'

    face_id: int = db.Column('faceid', db.Integer)
    group_id: int = db.Column('groupid', db.Integer)

    __mapper_args__ = {'primary_key': [face_id, group_id]}

    def multi_add(self, fids):
        with db.auto_commit_db():
            fgms = [FaceGroupMap(group_id=self.group_id, face_id=fid) for fid in fids]
            db.session.add_all(fgms)
        return

    def multi_delete(self, fids):
        with db.auto_commit_db():
            self.query.filter_by(group_id=self.group_id).filter(FaceGroupMap.face_id.in_(fids)).delete()
        return
