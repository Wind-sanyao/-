# !/usr/bin/env python
# -*- coding: utf-8 -*-
from praitek.app import db
from dataclasses import dataclass


@dataclass
class ObjectClass(db.Model):
    __tablename__ = 'objectclass'

    id: int = db.Column(db.Integer, primary_key=True)
    class_name: str = db.Column('classname', db.String)

    def get_object_class_list(self):
        return self.query.order_by(ObjectClass.id).all()
