from praitek.infra.event_rule import EventRule
from praitek.infra.stream_engine_map import StreamEngineMap


class DtoRule(object):
    id: int
    name: str
    rule: str
    disabled: int
    engine_id: int
    engine_name: str
    streams: list[dict]
    actions: list[dict]

    def __init__(self, rule_id: int, name: str, rule: str, disabled: int, engine_id: int, engine_name: str,
                 streams: list[dict], actions: list[dict]):
        self.id = rule_id
        self.name = name
        self.rule = rule
        self.disabled = disabled
        self.engine_id = engine_id
        self.engine_name = engine_name
        self.streams = streams
        self.actions = actions


class Rule(object):
    id: int
    name: str
    rule_str: str
    disabled: int

    def __init__(self, rule_id: int, name: str, rule: str, disabled: int):
        self.id = rule_id
        self.name = name
        self.rule_str = rule
        self.disabled = disabled

    @staticmethod
    def get_rules_by_stream_and_engine(stream_id: int, engine_ids: list[int],
                                       hide_disabled: bool = True) -> list["Rule"]:
        """
        Retrieve Rule by Stream and Engine

        :param stream_id: stream id
        :param engine_ids: engine id
        :param hide_disabled: 是否隐藏禁用的规则
        :return: 规则列表
        """
        rs: list["EventRule"] = []
        for engine_id in engine_ids:
            se_id = StreamEngineMap.get_seid_by_stream_and_engine(stream_id, engine_id)
            if se_id is None:
                continue
            event_rule_list = EventRule.get_rules_by_seid(se_id, hide_disabled)
            rs.extend(event_rule_list)

        return [Rule(r.id, r.name, r.rule, r.disabled) for r in rs]

    @staticmethod
    def get_rule_list():
        datas = EventRule.get_rule_list_with_engine()
        map_data = {}
        for rule in datas:
            engine_id = 0 if rule.engine_id is None else rule.engine_id
            stream_id = 0 if rule.stream_id is None else rule.stream_id
            key = f'{rule.id}_{engine_id}'
            if key in map_data:
                if stream_id != 0:
                    map_data[key].streams.append({'id': stream_id})
            else:
                if stream_id != 0:
                    streams = [{'id': rule.stream_id}]
                else:
                    streams = []
                map_data[key] = DtoRule(
                    rule_id=rule.id, name=rule.name, rule=rule.rule, disabled=rule.disabled, engine_id=engine_id,
                    engine_name='', streams=streams, actions=[])
        return map_data.values()

    @staticmethod
    def get_event_rule_info(rule_id):
        datas = EventRule.get_rule_info_with_engine(rule_id)
        rule = datas[0]
        streams = [{'id': rule.stream_id} for rule in datas]

        return DtoRule(
            rule_id=rule.id, name=rule.name, rule=rule.rule, disabled=rule.disabled, engine_id=rule.engine_id,
            engine_name='', streams=streams, actions=[])

    @staticmethod
    def add_event_rule_info(rule: DtoRule):
        return EventRule(name=rule.name, rule=rule.rule).add_event_rule_info(
            rule.engine_id, [s.get('id', 0) for s in rule.streams])

    @staticmethod
    def delete_event_rule_info(rule_id: int) -> None:
        return EventRule(id=rule_id).delete_event_rule_info()

    @staticmethod
    def update_event_rule_info(rule: DtoRule):
        map_data = {name: value for name, value in vars(rule).items() if
                    value is not None and name in {'name', 'rule', 'disabled'}}
        return EventRule(id=rule.id).update_event_rule_info(map_data, rule.engine_id,
                                                            [s.get('id', 0) for s in rule.streams])


def test_main():
    rs = Rule.get_rules_by_stream_and_engine(1, [1])
    for r in rs:
        print(r.id, r.name, r.rule_str, r.disabled)


if __name__ == "__main__":
    test_main()
