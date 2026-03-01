# !/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.parse

import requests
from flask import json

from praitek.app import app, log
from praitek.infra.action import Action as Action_infra


class ActionHttp:
    method: str
    url: str
    header: dict
    param: dict
    body: str

    def __init__(self, method: str, url: str, header: dict, param: dict, data: str):
        self.method = method
        self.url = url
        self.header = header
        self.param = param
        self.body = data
        return


class ActionMail:
    def __init__(self):
        return


class Action:
    id: int
    type: str
    http: ActionHttp
    mail: ActionMail

    def __init__(self, aid: int, action_type: str, http: ActionHttp, mail: ActionMail):
        self.id = aid
        self.type = action_type
        self.http = http
        self.mail = mail
        return

    @classmethod
    def send_notification(cls, rule_id, event_id, stream_name, event_time):
        actions = Action_infra.get_action_list_by_rule_id(rule_id)
        for (action, rule_id) in actions:
            log.debug(action)
            if action.type == 'http':
                req = eval(action.data)
                req['body'] = req['body'].replace('{{camera_name}}', stream_name).replace(
                    '{{event_timestamp}}', event_time.strftime('%a, %d %b %Y %H:%M:%S GMT')).replace(
                    '{{image_id}}', str(event_id)).replace('{{host_http_port}}', str(app.config.get('port', 8001)))
                log.debug(f'send http req: {req}')
                action_http = ActionHttp(method=req['method'], url=req['url'], header=req['header'], param=req['param'],
                                         data=req['body'])
                cls.send_http_notify(action_http)
        return

    @staticmethod
    def send_http_notify(action: ActionHttp):
        url = action.url
        data = json.loads(action.body)
        headers = action.header
        param = urllib.parse.urlencode(action.param)
        if action.method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=param)
        else:
            response = requests.post(url, headers=headers, params=param, json=data)
        log.debug('send notify get resp: %s', response.text)
        return

    @staticmethod
    def send_mail_notify(action: ActionMail):
        return

    def add_event_action_info(self, rule_id):
        data = self.http.__dict__ if self.type == 'http' else self.mail.__dict__
        return Action_infra(type=self.type, data=data.__str__()).add_action(rule_id)

    @staticmethod
    def get_event_action_list_by_rule(rule_id):
        actions = Action_infra.get_action_list_by_rule_id(rule_id)
        return [action for (action, rule_id) in actions]


if __name__ == '__main__':
    from praitek.infra.event import Event

    ei = Event.get_event_by_id(1040)
    Action.send_notification(rule_id=13, event_id=ei.id, stream_name=ei.stream_name, event_time=ei.timestamp)
    # Action.send_http_notify(ActionHttp(aid=0, method='POST', address='http://192.168.250.182:5099/analytics-events/OD',
    #                                    parameters='', data=body_str))
