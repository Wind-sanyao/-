import queue
import threading
import time
from typing import Callable

import cv2

from praitek.app import log
from praitek.domain.object_detection import od_predict
from praitek.domain.stream import StreamInfo
from praitek.service.ivatask import IvaTask


class ObjectDetectionService(threading.Thread):

    def __init__(self, queue_in: queue.Queue, callback: Callable[[IvaTask], None]):
        super().__init__()
        self.__q_in = queue_in
        self.__callback = callback
        self._stop_event = threading.Event()
        self.name = ObjectDetectionService.__name__
        self.daemon = True

    def run(self):
        self._stop_event.clear()

        while not self._stop_event.is_set():
            try:
                task: IvaTask = self.__q_in.get(timeout=0.5)
                task.boxes = od_predict(task.frame)
                self.__callback(task)
            except queue.Empty:
                pass
            finally:
                time.sleep(0.001)

        log.info(f"{self.name} stopped gracefully")

    def stop(self):
        self._stop_event.set()


def test_callback(task: IvaTask):
    print(f'callback: {task.datetime}')
    for box in task.boxes:
        print(f'{box.class_id} {box.class_name} {box.xyxy} {box.xywh}')
        cv2.rectangle(task.frame, box.xyxy[:2], box.xyxy[2:], (0, 255, 0), 2)
        cv2.putText(task.frame, f'{box.class_name} {box.confidence:.2f}', box.xyxy[:2], cv2.FONT_HERSHEY_SIMPLEX, 0.3,
                    (0, 0, 255), 1)
    cv2.imwrite('7_out.png', task.frame)


def test_main():
    q = queue.Queue(maxsize=100)
    t = ObjectDetectionService(q, test_callback)
    t.start()

    frame = cv2.imread('7.png')
    q.put(IvaTask(frame, StreamInfo(stream_id=1, name='test', stream_type='rtmp', stream_url='', owner_account_id=1,
                                    disabled=0)))
    time.sleep(1.0)
    t.stop()


if __name__ == '__main__':
    test_main()
