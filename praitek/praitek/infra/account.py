# !/usr/bin/env python
# -*- coding: utf-8 -*-
from praitek.app import db
from dataclasses import dataclass


@dataclass
class Account(db.Model):
    __tablename__ = 'account'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String)
    password: str = db.Column(db.String)
    disabled: int = db.Column(db.Integer, default=0)

    def get_info_by_name(self, name):
        return self.query.filter_by(name=name).first()
