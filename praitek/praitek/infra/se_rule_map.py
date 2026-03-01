# !/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from praitek.app import db


@dataclass
class StreamEngineRuleMap(db.Model):
    __tablename__ = 'se_rule_map'

    se_id: int = db.Column('seid', db.Integer)
    rule_id: int = db.Column('ruleid', db.Integer)

    __mapper_args__ = {'primary_key': [se_id, rule_id]}
