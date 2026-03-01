import unittest
from stream_engine_map import StreamEngineMap


class MyTestCase(unittest.TestCase):
    def test_add_map(self):
        mc1 = len(StreamEngineMap().get_map_list())
        m_id = StreamEngineMap(stream_id=0, engine_id=0).add_stream_engine_map()
        mc2 = len(StreamEngineMap().get_map_list())
        StreamEngineMap(id=m_id).delete_stream_engine_map()
        mc3 = len(StreamEngineMap().get_map_list())

        self.assertEqual(mc1+1, mc2)
        self.assertEqual(mc1, mc3)


if __name__ == '__main__':
    unittest.main()
