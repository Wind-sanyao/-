# !/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, request, make_response
from flask_jwt_extended import jwt_required
from pre_request import pre

from praitek.router.base import Resp
from praitek.router.parser import get_event_list_params, add_event_rule_info_params
from praitek.service.rule import EventRuleService
from praitek.service.event import EventService
from praitek.service.action import EventActionService
from praitek.domain.rule import DtoRule
from praitek.domain.action import Action, ActionHttp, ActionMail

event_bp = Blueprint('event', __name__)


# 获取事件列表
@event_bp.route('/event/list', methods=['GET'])
@jwt_required()
@pre.catch(get_event_list_params)
def get_event_list():
    type_ = int(request.args.get('type', 0))
    filter_str = request.args.get('keyword', '')
    order_by = request.args.get('order_by')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 30))
    rst, cnt = EventService.get_event_list(type_, filter_str, order_by, page, size)
    return Resp(data={'list': rst, 'total': cnt}).to_dict()


# 获取事件图片
@event_bp.route('/event/image', methods=['GET'])
# @jwt_required()
def get_event_image():
    event_id = int(request.args.get('id'))
    with_bbox = int(request.args.get('with_bbox', 0))
    img = EventService.get_event_image(event_id, with_bbox)
    res = make_response(img)
    res.headers["Content-Type"] = "image/png"
    return res


# 获取事件规则列表
@event_bp.route('/event/rule/list', methods=['GET'])
@jwt_required()
def get_event_rule_list():
    return Resp(data={'list': EventRuleService.get_event_rule_list()}).to_dict()


# 获取事件规则
@event_bp.route('/event/rule/info', methods=['GET'])
@jwt_required()
def get_event_rule_info():
    rule_id = int(request.args.get('id'))
    return Resp(data=EventRuleService.get_event_rule_info(rule_id)).to_dict()


# 创建事件规则
@event_bp.route('/event/rule/info', methods=['POST'])
@jwt_required()
@pre.catch(add_event_rule_info_params)
def add_event_rule_info():
    rule = DtoRule(
        rule_id=0,
        name=request.json.get('name'),
        rule=request.json.get('rule'),
        disabled=request.json.get('disabled'),
        engine_id=request.json.get('engine_id'),
        engine_name='',
        streams=[{'id': sid} for sid in request.json.get('stream_ids')],
        actions=[]
    )
    return Resp(data={'id': EventRuleService.add_event_rule_info(rule)}).to_dict()


# 删除事件规则
@event_bp.route('/event/rule/info', methods=['DELETE'])
@jwt_required()
def delete_event_rule_info():
    rule_id = int(request.args.get('id'))
    EventRuleService.delete_event_rule_info(rule_id)
    return Resp().to_dict()


# 修改事件规则
@event_bp.route('/event/rule/info', methods=['PUT'])
@jwt_required()
def update_event_rule_info():
    rule = DtoRule(
        rule_id=request.json.get('id'),
        name=request.json.get('name'),
        rule=request.json.get('rule'),
        disabled=request.json.get('disabled'),
        engine_id=request.json.get('engine_id'),
        engine_name='',
        streams=[{'id': sid} for sid in request.json.get('stream_ids')],
        actions=[]
    )
    EventRuleService.update_event_rule_info(rule)
    return Resp().to_dict()


# 创建事件处理规则
@event_bp.route('/event/action/info', methods=['POST'])
@jwt_required()
def add_event_action_info():
    rule_id = request.json.get('rule_id'),
    http = ActionHttp(
        url=request.json.get('url'),
        method=request.json.get('method'),
        header=request.json.get('header'),
        param=request.json.get('param'),
        data=request.json.get('body'),
    )
    mail = ActionMail()
    action = Action(
        aid=0,
        action_type=request.json.get('type'),
        http=http,
        mail=mail
    )
    return Resp(data={'id': EventActionService.add_event_action_info(action, rule_id)}).to_dict()


# 删除事件处理规则
@event_bp.route('/event/action/info', methods=['DELETE'])
@jwt_required()
def delete_event_action_info():
    action_id = int(request.args.get('id'))
    EventActionService.delete_event_action_info(action_id)
    return Resp().to_dict()
