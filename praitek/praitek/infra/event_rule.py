# !/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from praitek.app import db, app
from praitek.infra.se_rule_map import StreamEngineRuleMap
from praitek.infra.stream_engine_map import StreamEngineMap
from praitek.infra.rule_action_map import RuleActionMap
from praitek.infra.action import Action


@dataclass
class EventRule(db.Model):
    __tablename__ = 'eventrule'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String)
    rule: str = db.Column(db.String)
    disabled: int = db.Column(db.Integer, default=0)

    @staticmethod
    def get_rules_by_seid(se_id: int, hide_disabled: bool) -> list["EventRule"]:
        with app.app_context():
            # sql = f"select b.* from se_rule_map as TA, eventrule as b where TA.ruleid=b.id and TA.seid={se_id}"
            # if hide_disabled:
            #     sql += " and b.disabled=0"
            # return db.session.execute(sa.text(sql)).all()
            rs = db.session.query(EventRule).join(
                StreamEngineRuleMap, EventRule.id == StreamEngineRuleMap.rule_id).filter(
                StreamEngineRuleMap.se_id == se_id)
            if hide_disabled:
                rs = rs.filter(EventRule.disabled == 0)
            rs = rs.all()
            return rs

    @staticmethod
    def get_rule_list_with_engine():
        return (db.session.query(EventRule.id, EventRule.name, EventRule.rule, EventRule.disabled,
                                 StreamEngineMap.engine_id, StreamEngineMap.stream_id).
                outerjoin(StreamEngineRuleMap, EventRule.id == StreamEngineRuleMap.rule_id).
                outerjoin(StreamEngineMap, StreamEngineRuleMap.se_id == StreamEngineMap.id).all())

    @staticmethod
    def get_rule_info_with_engine(rule_id):
        return (db.session.query(EventRule.id, EventRule.name, EventRule.rule, EventRule.disabled,
                                 StreamEngineMap.engine_id, StreamEngineMap.stream_id).
                outerjoin(StreamEngineRuleMap, EventRule.id == StreamEngineRuleMap.rule_id).
                outerjoin(StreamEngineMap, StreamEngineRuleMap.se_id == StreamEngineMap.id).
                filter(EventRule.id == rule_id).all())

    def add_event_rule_info(self, engine_id, stream_ids):
        sem_ids = [m.id for m in StreamEngineMap.query.filter_by(engine_id=engine_id).filter(
            StreamEngineMap.stream_id.in_(stream_ids)).all()]
        with db.auto_commit_db():
            db.session.add(self)
            db.session.flush()
            rid = self.id
            serms = [StreamEngineRuleMap(se_id=se_id, rule_id=self.id) for se_id in sem_ids]
            db.session.add_all(serms)
        return rid

    def delete_event_rule_info(self):
        aids = [e.action_id for e in db.session.query(RuleActionMap.action_id).filter_by(rule_id=self.id).all()]
        with db.auto_commit_db():
            self.query.filter_by(id=self.id).delete()
            StreamEngineRuleMap.query.filter_by(rule_id=self.id).delete()
            RuleActionMap.query.filter_by(rule_id=self.id).delete()
            Action.query.filter(Action.id.in_(aids)).delete()
        return

    def update_event_rule_info(self, map_data, engine_id, stream_ids):
        sem_ids = [m.id for m in StreamEngineMap.query.filter_by(engine_id=engine_id).filter(
            StreamEngineMap.stream_id.in_(stream_ids)).all()]
        with db.auto_commit_db():
            self.query.filter_by(id=self.id).update(map_data)
            StreamEngineRuleMap.query.filter_by(rule_id=self.id).delete()
            serms = [StreamEngineRuleMap(se_id=se_id, rule_id=self.id) for se_id in sem_ids]
            db.session.add_all(serms)
        return

    def get_rule_by_name(self) -> "EventRule":
        with app.app_context():
            return self.query.filter_by(name=self.name).first()


def test_main():
    rule = EventRule(name="RULE FISH").get_rule_by_name()
    print(rule)


if __name__ == '__main__':
    test_main()
