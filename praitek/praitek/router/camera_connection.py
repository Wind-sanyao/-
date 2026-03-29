# !/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, request, make_response, send_from_directory
from praitek.router.base import Resp
from praitek.service.camera_connection import CameraConnectionService
from praitek.app import app, log

camera_connection_bp = Blueprint('camera_connection', __name__)


@camera_connection_bp.route('/camera_connection/bind', methods=['POST'])
def bind_camera():
    data = request.json
    camera_type = data.get('camera_type')
    camera_name = data.get('camera_name')
    
    if not camera_type or not camera_name:
        return Resp(success=False, error='缺少必要参数').to_dict()
    
    service = CameraConnectionService.instance()
    
    if camera_type == 'usb':
        device_index = data.get('device_index', '0')
        result = service.bind_camera(camera_type, camera_name, device_index=device_index)
    elif camera_type == 'rtsp':
        ip = data.get('ip', '')
        port = data.get('port', '554')
        username = data.get('username', '')
        password = data.get('password', '')
        brand = data.get('brand', 'Hikvision')
        model = data.get('model', 'Unknown')
        
        result = service.bind_camera(
            camera_type, camera_name,
            ip=ip, port=port, username=username,
            password=password, brand=brand, model=model
        )
    else:
        return Resp(success=False, error='不支持的摄像头类型').to_dict()
    
    if result['success']:
        return Resp(data={
            'session_id': result['session_id'],
            'camera_name': result['camera_name']
        }).to_dict()
    else:
        return Resp(success=False, error=result['error']).to_dict()


@camera_connection_bp.route('/camera_connection/snapshot/<session_id>', methods=['GET'])
def get_snapshot(session_id):
    service = CameraConnectionService.instance()
    frame = service.get_snapshot(session_id)
    
    if frame is None:
        res = make_response(b'')
        res.headers["Content-Type"] = "image/jpeg"
        return res
    
    res = make_response(frame)
    res.headers["Content-Type"] = "image/jpeg"
    res.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    res.headers["Pragma"] = "no-cache"
    res.headers["Expires"] = "0"
    return res


@camera_connection_bp.route('/camera_connection/info/<session_id>', methods=['GET'])
def get_camera_info(session_id):
    service = CameraConnectionService.instance()
    info = service.get_camera_info(session_id)
    
    if info is None:
        return Resp(success=False, error='会话不存在或已过期').to_dict()
    
    return Resp(data=info).to_dict()


@camera_connection_bp.route('/camera_connection/release/<session_id>', methods=['POST'])
def release_session(session_id):
    service = CameraConnectionService.instance()
    service.release_session(session_id)
    return Resp().to_dict()


@camera_connection_bp.route('/camera_connection/bind', methods=['GET'])
def bind_page():
    return send_from_directory('static', 'camera_connection_bind.html')


@camera_connection_bp.route('/camera_connection/monitor', methods=['GET'])
def monitor_page():
    return send_from_directory('static', 'camera_connection_monitor.html')
