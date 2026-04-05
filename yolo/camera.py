import cv2
import threading
import queue
from datetime import datetime
import time
import os
from models import db, SystemLog

class VideoCapturer:
    def __init__(self, source_type, source_url, user_id):
        self.source_type = source_type
        self.source_url = source_url
        self.user_id = user_id
        self.cap = None
        self.frame_queue = queue.Queue(maxsize=10)
        self.running = False
        self.capture_thread = None
        self.last_error = None
        self.detected_frame = None
        self.last_detection_time = 0
        self.detection_interval = 0.5
        self.fire_detected = False
        self.detection_confidence = 0.0
        self.model = None
        # 模型加载失败不应该阻止摄像头连接
        try:
            self._load_model()
        except Exception as e:
            print(f"模型加载失败，但不影响摄像头连接: {e}")
        self.camera_name = "未知摄像头"
        print(f"初始化VideoCapturer: {source_type}, {source_url}")
        
    def _load_model(self):
        try:
            from ultralytics import YOLO
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, 'runs', 'detect_v2', 'weights', 'best.pt')
            
            print(f"Current directory: {current_dir}")
            print(f"Model path: {model_path}")
            
            if os.path.exists(model_path):
                print(f"Model file exists, size: {os.path.getsize(model_path)} bytes")
                self.model = YOLO(model_path)
                print(f"Fire detection model loaded from: {model_path}")
            else:
                print(f"Warning: Model not found at {model_path}")
        except Exception as e:
            print(f"Error loading fire detection model: {e}")
            import traceback
            traceback.print_exc()
    
    def _detect_fire(self, frame):
        if self.model is None:
            # 模型未加载，直接返回原始帧
            return frame, False, 0.0
        
        try:
            results = self.model(frame, conf=0.5, verbose=False)
            annotated_frame = results[0].plot()
            
            fire_detected = False
            max_confidence = 0.0
            
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = self.model.names[class_id]
                    
                    if 'fire' in class_name.lower() or 'smoke' in class_name.lower():
                        fire_detected = True
                        if confidence > max_confidence:
                            max_confidence = confidence
            
            if fire_detected:
                log = SystemLog(
                    user_id=self.user_id,
                    camera_name=self.camera_name,
                    event_type='fire_detected',
                    event_message=f'检测到火灾，置信度: {max_confidence:.2f}'
                )
                try:
                    db.session.add(log)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving fire detection log: {e}")
            
            return annotated_frame, fire_detected, max_confidence
        except Exception as e:
            print(f"Error during fire detection: {e}")
            # 检测失败，返回原始帧
            return frame, False, 0.0
    
    def start(self):
        try:
            if self.source_type == 'usb':
                print(f"尝试打开USB摄像头，设备索引: {self.source_url}")
                self.cap = cv2.VideoCapture(int(self.source_url))
            else:
                print(f"尝试打开网络摄像头，URL: {self.source_url}")
                self.cap = cv2.VideoCapture(self.source_url)
            
            if not self.cap.isOpened():
                error_msg = f"无法打开摄像头: {self.source_url}"
                print(error_msg)
                raise Exception(error_msg)
            
            print("摄像头打开成功")
            self.running = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            return True
        except Exception as e:
            error_msg = f"启动摄像头失败: {str(e)}"
            print(error_msg)
            self.last_error = error_msg
            return False
    
    def _capture_loop(self):
        while self.running:
            try:
                ret, frame = self.cap.read()
                if ret:
                    current_time = time.time()
                    
                    # 确保frame不为空
                    if frame is not None and frame.size > 0:
                        if current_time - self.last_detection_time >= self.detection_interval:
                            try:
                                annotated_frame, fire_detected, confidence = self._detect_fire(frame)
                                self.detected_frame = annotated_frame
                                self.fire_detected = fire_detected
                                self.detection_confidence = confidence
                                self.last_detection_time = current_time
                            except Exception as e:
                                print(f"火灾检测过程中出错: {e}")
                                # 即使检测出错，也要保存原始帧
                                self.detected_frame = frame
                        
                        if self.frame_queue.full():
                            self.frame_queue.get()
                        self.frame_queue.put(frame)
                    else:
                        print("获取到空帧")
                else:
                    self.last_error = "无法读取摄像头画面"
                    self.running = False
            except Exception as e:
                self.last_error = str(e)
                print(f"捕获循环出错: {e}")
                # 不要立即停止，尝试继续捕获
                time.sleep(0.1)
    
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
    
    def get_detected_frame(self):
        try:
            # 确保detected_frame不为空
            if self.detected_frame is not None and self.detected_frame.size > 0:
                print(f"获取检测画面，帧大小: {self.detected_frame.shape}")
                ret, jpeg = cv2.imencode('.jpg', self.detected_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                if ret:
                    print(f"成功编码帧，大小: {len(jpeg.tobytes())} 字节")
                    return jpeg.tobytes()
                else:
                    print("编码帧失败")
            else:
                print("detected_frame为空或大小为0")
                # 尝试返回原始帧
                return self.get_frame()
            return None
        except Exception as e:
            self.last_error = str(e)
            print(f"获取检测画面出错: {e}")
            # 尝试返回原始帧
            return self.get_frame()
    
    def get_detection_status(self):
        return {
            'fire_detected': self.fire_detected,
            'confidence': self.detection_confidence,
            'last_detection_time': self.last_detection_time
        }
    
    def set_camera_name(self, name):
        self.camera_name = name