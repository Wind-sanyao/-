import cv2
import threading
import queue
from datetime import datetime

class VideoCapturer:
    def __init__(self, source_type, source_url):
        self.source_type = source_type
        self.source_url = source_url
        self.cap = None
        self.frame_queue = queue.Queue(maxsize=10)
        self.running = False
        self.capture_thread = None
        self.last_error = None
        
    def start(self):
        try:
            if self.source_type == 'usb':
                self.cap = cv2.VideoCapture(int(self.source_url))
            else:
                self.cap = cv2.VideoCapture(self.source_url)
            
            if not self.cap.isOpened():
                raise Exception("无法打开摄像头")
            
            self.running = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def _capture_loop(self):
        while self.running:
            try:
                ret, frame = self.cap.read()
                if ret:
                    if self.frame_queue.full():
                        self.frame_queue.get()
                    self.frame_queue.put(frame)
                else:
                    self.last_error = "无法读取摄像头画面"
                    self.running = False
            except Exception as e:
                self.last_error = str(e)
                self.running = False
    
    def get_frame(self):
        try:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                if ret:
                    return jpeg.tobytes()
            return None
        except Exception as e:
            self.last_error = str(e)
            return None
    
    def stop(self):
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1)
        if self.cap:
            self.cap.release()
    
    def get_error(self):
        return self.last_error
