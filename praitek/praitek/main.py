# !/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from praitek.app import app, log
from praitek.router import register_router
from praitek.service.biz import create_service, stop_service

if __name__ == '__main__':
    try:
        log.info('register routers')
        register_router(app)

        log.info('starting praitek kernel')
        create_service()

        signal.signal(signal.SIGINT, stop_service)
    except Exception as e:
        log.fatal(e)
    else:
        app.run(host='0.0.0.0', port=app.config.get('port', 8001), debug=True, use_reloader=False)
        log.info('goodbye!')
