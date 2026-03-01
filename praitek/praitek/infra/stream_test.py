import unittest
from stream import Stream
from stream_engine_map import StreamEngineMap


class MyTestCase(unittest.TestCase):
    def test_add_delete_stream(self):
        c1 = len(Stream().get_stream_list())
        s1 = Stream(name='stream_test1', source_type='rtsp', source_url='111', account_id=1)
        se_maps = [StreamEngineMap(engine_id=1), StreamEngineMap(engine_id=2)]
        sid = Stream.add_stream(s1, se_maps)
        c2 = len(Stream().get_stream_list())
        s1.id = sid
        s1.delete_stream()
        c3 = len(Stream().get_stream_list())

        self.assertEqual(c1 + 1, c2)
        self.assertEqual(c1, c3)

    def test_modify_stream(self):
        s1 = Stream(name='stream_test1', source_type='rtsp', source_url='111', account_id=1)
        se_maps = [StreamEngineMap(engine_id=1), StreamEngineMap(engine_id=2)]
        sid = Stream.add_stream(s1, se_maps)
        s1 = Stream(id=sid).get_stream_info()
        s1.modify_stream({'source_url': 'test url'})
        s1 = Stream(id=sid).get_stream_info()
        s1.id = sid
        s1.delete_stream()

        self.assertEqual(s1.source_url, 'test url')


if __name__ == '__main__':
    unittest.main()
