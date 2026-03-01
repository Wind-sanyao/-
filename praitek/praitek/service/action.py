# !/usr/bin/env python
# -*- coding: utf-8 -*-
from praitek.domain.action import Action as Action_domain
from praitek.infra.action import Action as Action_infra


class EventActionService:
    @staticmethod
    def add_event_action_info(action, rule_id):
        return action.add_event_action_info(rule_id)

    @staticmethod
    def delete_event_action_info(action_id):
        return Action_infra(id=action_id).delete_action()
