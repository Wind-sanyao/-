# !/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
import cv2
from typing import Optional
from praitek.app import log, db
from praitek.domain.stream import StreamInfo, VideoCapturer
from praitek.infra.stream import Stream as Stream_infra


class CameraConnectionService:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self.__active_sessions = {}

    @staticmethod
    def instance():
        return CameraConnectionService()

    def bind_camera(self, camera_type: str, camera_name: str, **kwargs) -> dict:
        session_id = str(uuid.uuid4())
        
        if camera_type == 'usb':
            device_index = kwargs.get('device_index', '0')
            source_type = 'usb'
            source_url = device_index
        elif camera_type == 'rtsp':
            ip = kwargs.get('ip', '')
            port = kwargs.get('port', '554')
            username = kwargs.get('username', '')
            password = kwargs.get('password', '')
            brand = kwargs.get('brand', 'Hikvision')
            model = kwargs.get('model', 'Unknown')
            
            rtsp_url = self._build_rtsp_url(ip, port, username, password, brand, model)
            source_type = 'rtsp'
            source_url = rtsp_url
        else:
            raise ValueError(f"Unsupported camera type: {camera_type}")
        
        stream_info = StreamInfo(
            stream_id=0,
            name=camera_name,
            stream_type=source_type,
            stream_url=source_url,
            owner_account_id=0,
            disabled=0
        )
        
        capturer = VideoCapturer(stream_info)
        try:
            success = capturer.start()
            if not success:
                return {
                    'success': False,
                    'error': '无法连接到摄像头，请检查配置信息'
                }
            
            frame = capturer.snapshot(timeout=2.0)
            if frame is None:
                capturer.stop()
                return {
                    'success': False,
                    'error': '无法获取摄像头画面，请检查摄像头是否正常工作'
                }
            
            capturer.stop()
            
            si = Stream_infra(
                name=camera_name,
                source_type=source_type,
                source_url=source_url,
                account_id=0,
                disabled=0
            )
            
            with db.auto_commit_db():
                db.session.add(si)
                db.session.flush()
                stream_id = si.id
            
            self.__active_sessions[session_id] = {
                'stream_id': stream_id,
                'camera_name': camera_name,
                'source_type': source_type,
                'source_url': source_url,
                'capturer': None
            }
            
            return {
                'success': True,
                'session_id': session_id,
                'camera_name': camera_name
            }
            
        except Exception as e:
            log.error(f"Failed to bind camera: {e}")
            return {
                'success': False,
                'error': f'绑定摄像头失败: {str(e)}'
            }

    def get_snapshot(self, session_id: str) -> Optional[bytes]:
        if session_id not in self.__active_sessions:
            return None
        
        session_data = self.__active_sessions[session_id]
        
        if session_data['capturer'] is None:
            stream_info = StreamInfo(
                stream_id=session_data['stream_id'],
                name=session_data['camera_name'],
                stream_type=session_data['source_type'],
                stream_url=session_data['source_url'],
                owner_account_id=0,
                disabled=0
            )
            capturer = VideoCapturer(stream_info)
            success = capturer.start()
            if not success:
                return None
            session_data['capturer'] = capturer
        
        capturer = session_data['capturer']
        frame = capturer.snapshot(timeout=1.0)
        
        if frame is None:
            return None
        
        frame_resized = cv2.resize(frame, (640, 480))
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
        _, img_encoded = cv2.imencode('.jpg', frame_resized, encode_param)
        
        return img_encoded.tobytes()

    def get_camera_info(self, session_id: str) -> Optional[dict]:
        if session_id not in self.__active_sessions:
            return None
        
        return {
            'camera_name': self.__active_sessions[session_id]['camera_name'],
            'source_type': self.__active_sessions[session_id]['source_type']
        }

    def release_session(self, session_id: str):
        if session_id in self.__active_sessions:
            session_data = self.__active_sessions[session_id]
            if session_data['capturer'] is not None:
                session_data['capturer'].stop()
            del self.__active_sessions[session_id]

    def _build_rtsp_url(self, ip: str, port: str, username: str, password: str, brand: str, model: str) -> str:
        from praitek.domain.camera import camera_map
        
        rtsp_template = 'rtsp://{username}:{password}@{ip}:{port}/Streaming/Channels/1'
        
        if brand in camera_map:
            models = camera_map[brand]
            for model_name, template in models:
                if model_name == model or model_name == 'Unknown':
                    rtsp_template = template
                    break
        
        rtsp_url = rtsp_template.format(
            username=username,
            password=password,
            ip=ip,
            port=port
        )
        
        return rtsp_url
