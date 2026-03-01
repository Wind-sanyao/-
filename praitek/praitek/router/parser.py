# !/usr/bin/env python
# -*- coding: utf-8 -*-
from pre_request import Rule

user_login_params = {
    'username': Rule(type=str, required=True, location='json'),
    'password': Rule(type=str, required=True, location='json'),
}

get_event_list_params = {
    'type': Rule(type=int, required=False, location='args'),
    'keyword': Rule(type=str, required=False, location='args'),
    'order_by': Rule(type=str, required=False, location='args'),
    'page': Rule(type=int, required=False, location='args'),
    'size': Rule(type=int, required=False, location='args'),
}

add_event_rule_info_params = {
    'name': Rule(type=str, required=True, location='json'),
    'rule': Rule(type=str, required=True, location='json', reg=r"^[a-zA-Z0-9_\(\)><=\-! ]+$"),
    'disabled': Rule(type=int, required=True, location='json'),
    'engine_id': Rule(type=int, required=True, location='json'),
    'stream_ids': Rule(type=int, required=True, location='json', multi=True),
}
