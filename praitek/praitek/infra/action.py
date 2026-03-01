# !/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from praitek.app import db
from praitek.infra.rule_action_map import RuleActionMap


@dataclass
class Action(db.Model):
    __tablename__ = 'action'

    id: int = db.Column(db.Integer, primary_key=True)
    type: str = db.Column('type', db.String)
    data: str = db.Column(db.Text)

    def add_action(self, rule_id):
        with db.auto_commit_db():
            db.session.add(self)
            db.session.flush()
            db.session.add(RuleActionMap(rule_id=rule_id, action_id=self.id))
        return self.id

    def delete_action(self):
        with db.auto_commit_db():
            self.query.filter_by(id=self.id).delete()
            RuleActionMap.query.filter_by(action_id=self.id).delete()
        return

    @staticmethod
    def get_action_list_by_rule_id(rule_id):
        return (db.session.query(Action, RuleActionMap.rule_id).
                join(RuleActionMap, Action.id == RuleActionMap.action_id).
                filter(RuleActionMap.rule_id == rule_id).all())
