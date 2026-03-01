# !/usr/bin/env python
# -*- coding: utf-8 -*-
from praitek.infra.engine import Engine as Engine_infra


class EngineInfo:
    id: int
    name: str

    def __init__(self, engine_id: int, name: str):
        self.id = engine_id
        self.name = name

    @staticmethod
    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()


class Engine:
    def __init__(self):
        pass

    @staticmethod
    def get_engine_list() -> list[EngineInfo]:
        engines = Engine_infra().get_engines_list()
        return [EngineInfo(engine.id, engine.name) for engine in engines]

    @staticmethod
    def get_engine_by_stream_id(stream_id) -> list[EngineInfo]:
        engines = Engine_infra.get_engines_by_stream_id(stream_id)
        return [EngineInfo(engine.id, engine.name) for engine in engines]

    @staticmethod
    def get_engines_by_stream_ids(stream_ids) -> {int: list[dict]}:
        datas = Engine_infra.get_engines_by_stream_ids(stream_ids)
        map_data = {}
        for engine in datas:
            if engine.stream_id in map_data.keys():
                map_data[engine.stream_id].append(EngineInfo(engine.id, engine.name).__dict__)
            else:
                map_data[engine.stream_id] = [EngineInfo(engine.id, engine.name).__dict__]
        return map_data


def test_main():
    for engine in Engine.get_engine_by_stream_id(2):
        print(engine.id, ':', engine.name)


if __name__ == '__main__':
    test_main()
