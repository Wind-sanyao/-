# !/usr/bin/env python
# -*- coding: utf-8 -*-
from praitek.infra.object_class import ObjectClass as Ob_infra


class ObjectClass(object):
    id: int
    name: str

    def __init__(self, oid, class_name):
        self.id = oid
        self.name = class_name


class Object:

    @staticmethod
    def get_object_class_list():
        return [ObjectClass(oid=i.id, class_name=i.class_name) for i in Ob_infra().get_object_class_list()]
