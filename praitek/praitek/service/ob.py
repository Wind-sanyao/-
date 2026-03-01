# !/usr/bin/env python
# -*- coding: utf-8 -*-
from praitek.domain.object_class import Object as Ob_domain


class Object:

    @staticmethod
    def get_object_class_list():
        return [ob.__dict__ for ob in Ob_domain().get_object_class_list()]
