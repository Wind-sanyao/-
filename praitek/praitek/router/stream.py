# !/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request, Blueprint, make_response
from flask_jwt_extended import jwt_required

from praitek.router.base import Resp
from praitek.service.stream import StreamService
from praitek.domain.stream import StreamInfoWithEngine

stream_bp = Blueprint('stream', __name__)


# 获取视频流信息
@stream_bp.route('/stream/info', methods=['GET'])
@jwt_required()
def get_stream_info():
    stream_id = request.args.get('id')
    return Resp(data=StreamService.get_stream_info(stream_id)).to_dict()


# 获取视频流列表
@stream_bp.route('/stream/list', methods=['GET'])
@jwt_required()
def get_stream_list():
    return Resp(data={'list': StreamService.get_stream_list()}).to_dict()


# 用户添加视频流
@stream_bp.route('/stream/info', methods=['POST'])
@jwt_required()
def add_stream():
    sie = StreamInfoWithEngine(
        stream_id=0,
        name=request.json.get('name'),
        stream_type=request.json.get('source_type'),
        stream_url=request.json.get('source_url'),
        owner_account_id=request.json.get('account_id'),
        disabled=request.json.get('disabled'),
        engine_ids=request.json.get('engine_ids'),
    )

    return Resp(data={'id': StreamService.instance().add_stream(sie)}).to_dict()


# 用户更新视频流
@stream_bp.route('/stream/info', methods=['PUT'])
@jwt_required()
def update_stream():
    stream_id = request.json.get('id')
    account_id = request.json.get('account_id')
    sie = StreamInfoWithEngine(
        stream_id=stream_id,
        name=request.json.get('name'),
        stream_type=request.json.get('source_type'),
        stream_url=request.json.get('source_url'),
        disabled=request.json.get('disabled'),
        engine_ids=request.json.get('engine_ids'),
    )

    StreamService.instance().update_stream(stream_id, sie, account_id)
    return Resp().to_dict()


# 用户删除视频流
@stream_bp.route('/stream/info', methods=['DELETE'])
@jwt_required()
def delete_stream():
    stream_id = int(request.args.get('id'))
    account_id = int(request.args.get('account_id', 0))
    StreamService.instance().delete_stream(stream_id, account_id)
    return Resp().to_dict()


# 用户启用视频流
@stream_bp.route('/stream/activate', methods=['POST'])
@jwt_required()
def activate_stream():
    stream_id = request.json.get('id')
    account_id = request.json.get('account_id')

    StreamService.instance().activate_stream(stream_id, account_id)
    return Resp().to_dict()


# 用户禁用视频流
@stream_bp.route('/stream/deactivate', methods=['POST'])
@jwt_required()
def deactivate_stream():
    stream_id = request.json.get('id')
    account_id = request.json.get('account_id')
    StreamService.instance().deactivate_stream(stream_id, account_id)
    return Resp().to_dict()


# 获取视频流截图
@stream_bp.route('/stream/snapshot', methods=['GET'])
@jwt_required()
def get_snapshot():
    source_type = request.args.get('source_type')
    source_url = request.args.get('source_url')
    frame = StreamService.get_snapshot(source_type, source_url)
    res = make_response(frame)
    res.headers["Content-Type"] = "image/png"
    return res
