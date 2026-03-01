#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import request

from praitek.app import app, log
from praitek.router.router import router_bp
from praitek.router.stream import stream_bp
from praitek.router.face import face_bp
from praitek.router.event import event_bp


@app.before_request
def before_request():
    param = request.args if request.method in ['GET', 'DELETE'] \
        else request.json if request.headers.get('Content-Type') == 'application/json' \
        else ''
    log.info('%s, %s', request.url, param)


def register_router(proj_app):
    proj_app.register_blueprint(router_bp)
    proj_app.register_blueprint(stream_bp)
    proj_app.register_blueprint(face_bp)
    proj_app.register_blueprint(event_bp)

    return
