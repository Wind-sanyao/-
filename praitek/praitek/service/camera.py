# !/usr/bin/env python
# -*- coding: utf-8 -*-
from praitek.domain.camera import Camera as Camera_domain


class CameraService:
    @staticmethod
    def get_supported_camera():
        return Camera_domain().get_supported_camera()
