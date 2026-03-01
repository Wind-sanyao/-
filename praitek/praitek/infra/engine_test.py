import unittest
from engine import Engine


class EngineTestCase(unittest.TestCase):
    def test_get_list(self):
        engine = Engine()
        datas = engine.get_engines_by_stream_id(1)
        self.assertEqual(len(datas), 1)  # add assertion here


if __name__ == '__main__':
    unittest.main()
