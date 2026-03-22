#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import request

from praitek.app import app, log
from praitek.router.router import router_bp
from praitek.router.stream import stream_bp
from praitek.router.event import event_bp
from praitek.router.camera_connection import camera_connection_bp

try:
    from praitek.router.face import face_bp
    HAS_FACE = True
except ImportError:
    HAS_FACE = False
    log.warning('face module not available, face recognition features disabled')


@app.before_request
def before_request():
    param = request.args if request.method in ['GET', 'DELETE'] \
        else request.json if request.headers.get('Content-Type') == 'application/json' \
        else ''
    log.info('%s, %s', request.url, param)


def register_router(proj_app):
    proj_app.register_blueprint(router_bp)
    proj_app.register_blueprint(stream_bp)
    proj_app.register_blueprint(event_bp)
    proj_app.register_blueprint(camera_connection_bp)
    if HAS_FACE:
        proj_app.register_blueprint(face_bp)

    return
