# !/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Collection

from praitek.app import db
from praitek.infra.face_group_map import FaceGroupMap
from praitek.infra.face_image import FaceImage
from praitek.infra.face_image_map import FaceImageMap


@dataclass
class Face(db.Model):
    __tablename__ = 'face'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String)

    def get_face_list(self):
        return self.query.all()

    def get_face_info(self):
        return self.query.filter_by(id=self.id).first()

    def add_face_info(self):
        with db.auto_commit_db():
            db.session.add(self)
            db.session.flush()
            fid = self.id
        return fid

    def update_face_info(self, map_data):
        with db.auto_commit_db():
            self.query.filter_by(id=self.id).update(map_data)

    def delete_face_info(self):
        image_ids = [m.image_id for m in FaceImageMap.query.filter_by(face_id=self.id).all()]
        with db.auto_commit_db():
            Face.query.filter_by(id=self.id).delete()
            FaceGroupMap.query.filter_by(face_id=self.id).delete()
            if len(image_ids) != 0:
                FaceImage.query.filter(FaceImage.id.in_(image_ids)).delete()
                FaceImageMap.query.filter_by(face_id=self.id).delete()

    @staticmethod
    def get_face_list_by_group_ids(ids: Collection[int]):
        """
        返回一个list，其中每个元素是tuple(face_id, face_name, group_id)
        :param ids:
        :return:
        """
        return db.session.query(Face.id, Face.name, FaceGroupMap.group_id).join(
            FaceGroupMap, Face.id == FaceGroupMap.face_id).filter(FaceGroupMap.group_id.in_(ids)).all()


if __name__ == '__main__':
    faces = Face.get_face_list_by_group_ids([2, 3])
    print(faces)
