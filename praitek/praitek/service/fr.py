import queue
import threading
import time
from typing import Callable

from praitek.app import log
from praitek.domain.face_recognize import face_predict
from praitek.service.ivatask import IvaTask


class FaceRecognitionService(threading.Thread):

    def __init__(self, queue_in: queue.Queue, callback: Callable[[IvaTask], None]):
        super().__init__()
        self.__q_in = queue_in
        self.__callback = callback
        self._stop_event = threading.Event()
        self.name = FaceRecognitionService.__name__
        self.daemon = True

    def run(self):
        self._stop_event.clear()

        while not self._stop_event.is_set():
            try:
                task: IvaTask = self.__q_in.get(timeout=0.5)
            except queue.Empty:
                pass
            else:
                task.boxes = face_predict(task.frame)
                self.__callback(task)
            finally:
                time.sleep(0.001)

        log.info(f"{self.name} stopped gracefully")

    def stop(self):
        self._stop_event.set()
