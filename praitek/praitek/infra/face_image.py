# !/usr/bin/env python
# -*- coding: utf-8 -*-
from praitek.app import db
from dataclasses import dataclass

from praitek.infra.face_image_map import FaceImageMap


@dataclass
class FaceImage(db.Model):
    __tablename__ = 'faceimage'

    id: int = db.Column(db.Integer, primary_key=True)
    image: str = db.Column(db.String)

    # todo: 待测试并发
    @staticmethod
    def multi_add_face_image_info(fid, images: list[str]):
        with db.auto_commit_db():
            # 一失败全失败
            result = db.session.execute(FaceImage.__table__.insert(), [{'image': s} for s in images])
            db.session.commit()

            last_insert_id = result.lastrowid
            end_insert_id = last_insert_id + len(images)
            ids = list(range(last_insert_id, end_insert_id))
            fgm = [FaceImageMap(face_id=fid, image_id=iid) for iid in ids]
            db.session.add_all(fgm)
        return

    @staticmethod
    def multi_delete_face_image_info(face_id, img_ids):
        with db.auto_commit_db():
            FaceImage.query.filter(FaceImage.id.in_(img_ids)).delete()
            FaceImageMap.query.filter_by(face_id=face_id).filter(FaceImageMap.image_id.in_(img_ids)).delete()
        return

    @staticmethod
    def get_image_list_by_face_list(ids):
        return (db.session.query(FaceImage.id, FaceImage.image, FaceImageMap.face_id).
                join(FaceImageMap, FaceImage.id == FaceImageMap.image_id).
                filter(FaceImageMap.face_id.in_(ids)).order_by(FaceImageMap.face_id, FaceImage.id).all())

    def get_face_image_info(self):
        return (db.session.query(FaceImage.image, FaceImageMap.face_id).
                join(FaceImageMap, FaceImage.id == FaceImageMap.image_id).
                filter(FaceImage.id == self.id).first())

    @staticmethod
    def get_image_list_of_face(face_id, image_ids):
        return (db.session.query(FaceImage.id, FaceImage.image).
                join(FaceImageMap, FaceImage.id == FaceImageMap.image_id).
                filter(FaceImageMap.face_id == face_id).filter(FaceImageMap.image_id.in_(image_ids)).all())
