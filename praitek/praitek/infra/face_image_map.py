# !/usr/bin/env python
# -*- coding: utf-8 -*-
from praitek.app import db
from dataclasses import dataclass


@dataclass
class FaceImageMap(db.Model):
    __tablename__ = 'face_image_map'

    face_id: int = db.Column('faceid', db.Integer)
    image_id: int = db.Column('imageid', db.Integer)

    __mapper_args__ = {'primary_key': [face_id, image_id]}
