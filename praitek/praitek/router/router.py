#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import request, Blueprint
from flask_jwt_extended import create_access_token, jwt_required
from pre_request import pre

from praitek.router.base import Resp
from praitek.router.parser import user_login_params
from praitek.service.user import User as User_service
from praitek.service.ob import Object as Ob_service
from praitek.service.engine import Engine as Engine_service
from praitek.service.camera import CameraService as Camera_service

router_bp = Blueprint('router', __name__)


# 用户登陆
@router_bp.route('/user/login', methods=['POST'])
@pre.catch(user_login_params)
def user_login():
    username = request.json.get('username')
    pwd = request.json.get('password')
    ok, uid = User_service(username, pwd).user_login()
    if ok:
        token = create_access_token(identity=username)
        return Resp(data={'token': token, 'user_id': uid}).to_dict()
    return Resp(code=1).to_dict()


# 获取分析目标类列表
@router_bp.route('/object/list', methods=['GET'])
@jwt_required()
def get_object_list():
    return Resp(data={'list': Ob_service.get_object_class_list()}).to_dict()


# 获取引擎列表
@router_bp.route('/engine/list', methods=['GET'])
@jwt_required()
def get_engine_list():
    return Resp(data={'list': Engine_service.get_engine_list()}).to_dict()


# 获取支持的摄像头型号
@router_bp.route('/camera/supported', methods=['GET'])
@jwt_required()
def get_supported_camera():
    return Resp(data=Camera_service.get_supported_camera()).to_dict()
