# !/usr/bin/env python
# -*- coding: utf-8 -*-
from praitek.domain.engine import Engine as Engine_domain


class Engine:
    @staticmethod
    def get_engine_list():
        return [engine.__dict__ for engine in Engine_domain().get_engine_list()]
