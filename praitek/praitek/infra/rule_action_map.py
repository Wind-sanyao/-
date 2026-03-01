# !/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from praitek.app import db


@dataclass
class RuleActionMap(db.Model):
    __tablename__ = 'rule_action_map'

    rule_id: int = db.Column('ruleid', db.Integer)
    action_id: int = db.Column('actionid', db.Integer)

    __mapper_args__ = {'primary_key': [rule_id, action_id]}
