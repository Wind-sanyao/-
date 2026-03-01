# !/usr/bin/env python
# -*- coding: utf-8 -*-


class Resp:
    def __init__(self, code: int = 0, msg: str = '', data: dict = None):
        self.code = code
        self.msg = msg
        if data is None:
            data = {}
        try:
            self.data = self.serialize(data)
        except SerializationError as e:
            self.code = e.code
            self.msg = e.msg

    @staticmethod
    def serialize(obj):
        if obj is None:
            return {}
        try:
            # 如果对象本身就是可以序列化为JSON的类型，则直接返回
            if isinstance(obj, (str, int, float, bool, list, tuple, dict)):
                return obj
            # # 如果对象是ORM对象，则将其转换为字典并返回
            # elif isinstance(obj.__class__, DeclarativeMeta):
            #     return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            # 如果对象实现了__dict__方法，则将其转换为字典并返回
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            # 如果对象是其他类型，则抛出异常
            else:
                raise SerializationError(code=500, msg='Cannot serialize object')
        except Exception as e:
            raise SerializationError(code=500, msg=str(e))

    def to_dict(self):
        return self.__dict__


class SerializationError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
