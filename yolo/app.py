from flask import Flask, request, jsonify, Response, render_template, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
import os
import hashlib
from models import db, User, CameraInfo, Stream, SystemLog, UserSetting
from camera import VideoCapturer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
CORS(app)
app.secret_key = 'fire_detection_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fire_detection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

capturers = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def require_login(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # 检查是否是API请求
            if request.path.startswith('/api/'):
                # 对于API请求，返回401状态码
                return jsonify({'error': '未登录或会话过期'}), 401
            else:
                # 对于普通页面请求，重定向到登录页面
                return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        setting = UserSetting.query.filter_by(user_id=user.id).first()
        return render_template('home.html', user=user, setting=setting)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        
        user = User.query.filter_by(phone=phone).first()
        if user and user.password == hash_password(password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        return render_template('login.html', error='手机号或密码错误')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['phone']
        password = request.form['password']
        
        existing_user = User.query.filter_by(phone=phone).first()
        if existing_user:
            return render_template('register.html', error='该手机号已注册')
        
        new_user = User(
            username=username,
            phone=phone,
            password=hash_password(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        new_setting = UserSetting(user_id=new_user.id)
        db.session.add(new_setting)
        db.session.commit()
        
        session['user_id'] = new_user.id
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@require_login
def upload():
    user_id = session['user_id']
    user = User.query.get(user_id)
    setting = UserSetting.query.filter_by(user_id=user_id).first()
    
    if request.method == 'POST':
        try:
            # 检查是否有文件上传
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': '请选择文件'})
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'success': False, 'error': '请选择文件'})
            
            # 检查文件类型
            file_ext = os.path.splitext(file.filename)[1].lower()
            is_image = file_ext in ['.jpg', '.jpeg', '.png', '.gif']
            is_video = file_ext in ['.mp4', '.avi', '.mov', '.wmv']
            
            if not (is_image or is_video):
                return jsonify({'success': False, 'error': '不支持的文件类型'})
            
            # 保存文件
            upload_dir = os.path.join(BASE_DIR, 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            file_path = os.path.join(upload_dir, file.filename)
            file.save(file_path)
            
            # 处理文件
            if is_image:
                # 处理图片
                result = process_image(file_path)
            else:
                # 处理视频
                result = process_video(file_path)
            
            # 构建响应
            response = {
                'success': True,
                'file_name': file.filename,
                'file_type': '图片' if is_image else '视频',
                'file_size': f"{os.path.getsize(file_path) / 1024:.2f} KB",
                'is_image': is_image,
                'results': result
            }
            
            if is_image:
                response['fire_detected'] = result['fire_detected']
                response['confidence'] = result['confidence']
                # 转换图片为base64
                with open(file_path, 'rb') as f:
                    import base64
                    response['image_data'] = base64.b64encode(f.read()).decode('utf-8')
            else:
                response['video_duration'] = result['duration']
                response['fire_timepoints'] = result['fire_timepoints']
            
            # 保存到会话，用于导出
            session['upload_result'] = response
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return render_template('upload.html', user=user, setting=setting)

@app.route('/settings', methods=['GET', 'POST'])
@require_login
def settings():
    user_id = session['user_id']
    user = User.query.get(user_id)
    setting = UserSetting.query.filter_by(user_id=user_id).first()
    
    if request.method == 'POST':
        theme = request.form['theme']
        font_size = request.form['font_size']
        
        setting.theme = theme
        setting.font_size = font_size
        db.session.commit()
        return render_template('settings.html', user=user, setting=setting, message='设置已保存')
    
    return render_template('settings.html', user=user, setting=setting)

@app.route('/bind', methods=['GET', 'POST'])
@require_login
def bind():
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # 获取用户自己的摄像头信息
    user_cameras = CameraInfo.query.filter_by(user_id=user_id).all()
    # 获取系统预录入的摄像头信息
    predefined_cameras = CameraInfo.query.filter_by(is_predefined=True).all()
    # 合并两种摄像头信息
    camera_infos = user_cameras + predefined_cameras
    
    if request.method == 'POST':
        camera_type = request.form['cameraType']
        name = request.form['cameraName']
        
        session_id = str(uuid.uuid4())
        source_url = ''
        
        if camera_type == 'usb':
            device_index = request.form['deviceIndex']
            source_url = str(device_index)
        elif camera_type == 'rtsp':
            ip = request.form['ipAddress']
            port = request.form['port']
            username = request.form['username']
            password = request.form['password']
            source_url = f'rtsp://{username}:{password}@{ip}:{port}/stream'
        
        stream = Stream(
            session_id=session_id,
            user_id=user_id,
            source_type=camera_type,
            source_url=source_url,
            name=name,
            status='connecting'
        )
        db.session.add(stream)
        db.session.commit()
        
        log = SystemLog(
            user_id=user_id,
            camera_name=name,
            event_type='camera_bound',
            event_message=f'绑定了新摄像头: {name}'
        )
        db.session.add(log)
        db.session.commit()
        
        capturer = VideoCapturer(camera_type, source_url, user_id)
        print(f"创建VideoCapturer实例: {camera_type}, {source_url}, {user_id}")
        
        # 设置摄像头名称
        capturer.set_camera_name(name)
        
        if capturer.start():
            print(f"摄像头启动成功，会话ID: {session_id}")
            capturers[session_id] = capturer
            stream.status = 'connected'
            stream.updated_at = datetime.utcnow()
            db.session.commit()
            print(f"重定向到监控页面: {session_id}")
            return redirect(url_for('monitor', session_id=session_id))
        else:
            error_info = capturer.get_error()
            print(f"摄像头启动失败: {error_info}")
            stream.status = 'error'
            stream.error_info = error_info
            db.session.commit()
            return render_template('bind.html', user=user, user_cameras=user_cameras, predefined_cameras=predefined_cameras, error='无法连接摄像头')
    
    return render_template('bind.html', user=user, user_cameras=user_cameras, predefined_cameras=predefined_cameras)

@app.route('/monitor/<session_id>')
@require_login
def monitor(session_id):
    user_id = session['user_id']
    user = User.query.get(user_id)
    stream = Stream.query.filter_by(session_id=session_id, user_id=user_id).first()
    
    if not stream:
        return redirect(url_for('bind'))
    
    return render_template('monitor.html', user=user, session_id=session_id, camera_name=stream.name)

@app.route('/api/camera/bind', methods=['POST'])
@require_login
def bind_camera():
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400
        
        camera_type = data.get('cameraType')
        name = data.get('name')
        
        if not camera_type or not name:
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400
        
        if len(name) > 50:
            return jsonify({'success': False, 'error': '摄像头名称不能超过50个字符'}), 400
        
        session_id = str(uuid.uuid4())
        source_url = ''
        
        if camera_type == 'usb':
            device_index = data.get('deviceIndex', 0)
            source_url = str(device_index)
        elif camera_type == 'rtsp':
            ip = data.get('ip')
            port = data.get('port', 554)
            username = data.get('username')
            password = data.get('password')
            
            if not ip or not username or not password:
                return jsonify({'success': False, 'error': '网络摄像头信息不完整'}), 400
            
            source_url = f'rtsp://{username}:{password}@{ip}:{port}/stream'
        else:
            return jsonify({'success': False, 'error': '无效的摄像头类型'}), 400
        
        stream = Stream(
            session_id=session_id,
            user_id=user_id,
            source_type=camera_type,
            source_url=source_url,
            name=name,
            status='connecting'
        )
        db.session.add(stream)
        db.session.commit()
        
        capturer = VideoCapturer(camera_type, source_url, user_id)
        if capturer.start():
            capturers[session_id] = capturer
            stream.status = 'connected'
            stream.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'sessionId': session_id})
        else:
            stream.status = 'error'
            stream.error_info = capturer.get_error()
            db.session.commit()
            return jsonify({'success': False, 'error': stream.error_info or '无法连接摄像头'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/camera/snapshot/<session_id>')
@require_login
def get_snapshot(session_id):
    try:
        user_id = session['user_id']
        stream = Stream.query.filter_by(session_id=session_id, user_id=user_id).first()
        
        if not stream:
            return jsonify({'error': '会话不存在'}), 404
        
        if stream.status != 'connected':
            return jsonify({'error': '摄像头未连接'}), 503
        
        if session_id not in capturers:
            return jsonify({'error': '摄像头连接已断开'}), 503
        
        capturer = capturers[session_id]
        frame_data = capturer.get_frame()
        
        if frame_data:
            stream.updated_at = datetime.utcnow()
            db.session.commit()
            
            response = Response(frame_data, mimetype='image/jpeg')
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        else:
            stream.status = 'error'
            stream.error_info = capturer.get_error() or '无法获取摄像头画面'
            db.session.commit()
            return jsonify({'error': stream.error_info}), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/detection/<session_id>')
@require_login
def get_detection_frame(session_id):
    try:
        user_id = session['user_id']
        stream = Stream.query.filter_by(session_id=session_id, user_id=user_id).first()
        
        if not stream:
            return jsonify({'error': '会话不存在'}), 404
        
        if stream.status != 'connected':
            return jsonify({'error': '摄像头未连接'}), 503
        
        if session_id not in capturers:
            return jsonify({'error': '摄像头连接已断开'}), 503
        
        capturer = capturers[session_id]
        
        # 检查摄像头是否有错误
        error = capturer.get_error()
        if error:
            stream.status = 'error'
            stream.error_info = error
            db.session.commit()
            return jsonify({'error': error}), 503
        
        frame_data = capturer.get_detected_frame()
        
        if frame_data:
            stream.updated_at = datetime.utcnow()
            db.session.commit()
            
            response = Response(frame_data, mimetype='image/jpeg')
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        else:
            # 尝试获取原始帧
            frame_data = capturer.get_frame()
            if frame_data:
                stream.updated_at = datetime.utcnow()
                db.session.commit()
                
                response = Response(frame_data, mimetype='image/jpeg')
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
            else:
                return jsonify({'error': '无法获取摄像头画面'}), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/detection/status/<session_id>')
@require_login
def get_detection_status(session_id):
    try:
        user_id = session['user_id']
        stream = Stream.query.filter_by(session_id=session_id, user_id=user_id).first()
        
        if not stream:
            return jsonify({'error': '会话不存在'}), 404
        
        if stream.status != 'connected':
            return jsonify({'error': '摄像头未连接'}), 503
        
        if session_id not in capturers:
            return jsonify({'error': '摄像头连接已断开'}), 503
        
        capturer = capturers[session_id]
        status = capturer.get_detection_status()
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/info/<session_id>')
@require_login
def get_camera_info(session_id):
    try:
        user_id = session['user_id']
        stream = Stream.query.filter_by(session_id=session_id, user_id=user_id).first()
        
        if not stream:
            return jsonify({'error': '会话不存在'}), 404
        
        return jsonify(stream.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/unbind/<session_id>', methods=['DELETE'])
@require_login
def unbind_camera(session_id):
    try:
        user_id = session['user_id']
        stream = Stream.query.filter_by(session_id=session_id, user_id=user_id).first()
        
        if stream:
            db.session.delete(stream)
            db.session.commit()
        
        if session_id in capturers:
            capturers[session_id].stop()
            del capturers[session_id]
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/camera/info/list')
@require_login
def get_camera_info_list():
    try:
        user_id = session['user_id']
        camera_infos = CameraInfo.query.filter_by(user_id=user_id).all()
        predefined_cameras = CameraInfo.query.filter_by(is_predefined=True).all()
        
        return jsonify({
            'user_cameras': [info.to_dict() for info in camera_infos],
            'predefined_cameras': [info.to_dict() for info in predefined_cameras]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/info/save', methods=['POST'])
@require_login
def save_camera_info():
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        new_camera = CameraInfo(
            user_id=user_id,
            name=data['name'],
            source_type=data['source_type'],
            source_url=data['source_url'],
            ip_address=data.get('ip_address'),
            port=data.get('port'),
            username=data.get('username'),
            password=data.get('password'),
            brand=data.get('brand'),
            model=data.get('model'),
            is_predefined=data.get('is_predefined', False)
        )
        db.session.add(new_camera)
        db.session.commit()
        
        return jsonify({'success': True, 'camera_id': new_camera.id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs/system')
@require_login
def get_system_logs():
    try:
        user_id = session['user_id']
        logs = SystemLog.query.filter_by(user_id=user_id).order_by(SystemLog.created_at.desc()).all()
        
        return jsonify([log.to_dict() for log in logs])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs/export')
@require_login
def export_logs():
    try:
        user_id = session['user_id']
        logs = SystemLog.query.filter_by(user_id=user_id).order_by(SystemLog.created_at.desc()).all()
        
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['时间', '摄像头', '事件类型', '详细信息'])
        
        for log in logs:
            writer.writerow([
                log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                log.camera_name,
                '火灾检测' if log.event_type == 'fire_detected' else '摄像头绑定',
                log.event_message
            ])
        
        output.seek(0)
        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=system_logs.csv'
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET', 'PUT'])
@require_login
def user_settings():
    try:
        user_id = session['user_id']
        setting = UserSetting.query.filter_by(user_id=user_id).first()
        
        if request.method == 'PUT':
            data = request.get_json()
            setting.theme = data.get('theme', setting.theme)
            setting.font_size = data.get('font_size', setting.font_size)
            db.session.commit()
            
        return jsonify(setting.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cameras', methods=['GET', 'POST', 'DELETE'])
@require_login
def manage_cameras():
    try:
        user_id = session['user_id']
        
        if request.method == 'GET':
            # 获取用户的摄像头信息和预录入摄像头
            user_cameras = CameraInfo.query.filter_by(user_id=user_id).all()
            # 获取系统预录入的摄像头信息（不包含用户自己的）
            predefined_cameras = CameraInfo.query.filter_by(is_predefined=True, user_id=None).all()
            cameras = user_cameras + predefined_cameras
            
            return jsonify([camera.to_dict() for camera in cameras])
        
        elif request.method == 'POST':
            # 添加新的预录入摄像头
            data = request.get_json()
            
            camera = CameraInfo(
                name=data['name'],
                source_type=data['cameraType'],
                source_url='',  # 保留字段但设置为空字符串
                ip_address=data.get('ipAddress'),
                port=data.get('port'),
                username=data.get('username'),
                password=data.get('password'),
                brand=data.get('brand'),
                model='',  # 保留字段但设置为空字符串
                user_id=user_id,  # 保留用户ID，以便区分不同用户的预录入摄像头
                is_predefined=True
            )
            
            db.session.add(camera)
            db.session.commit()
            
            return jsonify(camera.to_dict()), 201
        
        elif request.method == 'DELETE':
            # 删除摄像头
            camera_id = request.json.get('id')
            camera = CameraInfo.query.get(camera_id)
            
            if camera and camera.user_id == user_id:
                db.session.delete(camera)
                db.session.commit()
                return jsonify({'message': '摄像头已删除'})
            else:
                return jsonify({'error': '摄像头不存在或无权限删除'}), 403
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_image(file_path):
    """处理图片，检测是否有烟火"""
    try:
        import cv2
        from ultralytics import YOLO
        
        # 加载模型
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'runs', 'detect_v2', 'weights', 'best.pt')
        
        if os.path.exists(model_path):
            model = YOLO(model_path)
        else:
            # 如果模型不存在，返回默认结果
            return {'fire_detected': False, 'confidence': 0.0}
        
        # 读取图片
        img = cv2.imread(file_path)
        if img is None:
            return {'fire_detected': False, 'confidence': 0.0}
        
        # 检测
        results = model(img, conf=0.5, verbose=False)
        
        fire_detected = False
        max_confidence = 0.0
        
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names[class_id]
                
                if 'fire' in class_name.lower() or 'smoke' in class_name.lower():
                    fire_detected = True
                    if confidence > max_confidence:
                        max_confidence = confidence
        
        return {'fire_detected': fire_detected, 'confidence': max_confidence}
        
    except Exception as e:
        print(f"处理图片时出错: {e}")
        return {'fire_detected': False, 'confidence': 0.0}

def process_video(file_path):
    """处理视频，检测是否有烟火"""
    try:
        import cv2
        from ultralytics import YOLO
        
        # 加载模型
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'runs', 'detect_v2', 'weights', 'best.pt')
        
        if os.path.exists(model_path):
            model = YOLO(model_path)
        else:
            # 如果模型不存在，返回默认结果
            return {'duration': 0, 'fire_timepoints': []}
        
        # 打开视频
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return {'duration': 0, 'fire_timepoints': []}
        
        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = int(total_frames / fps) if fps > 0 else 0
        
        fire_timepoints = []
        frame_count = 0
        
        # 每秒检测一帧
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 每秒检测一帧
            if frame_count % int(fps) == 0:
                # 检测
                results = model(frame, conf=0.5, verbose=False)
                
                fire_detected = False
                for result in results:
                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        class_name = model.names[class_id]
                        
                        if 'fire' in class_name.lower() or 'smoke' in class_name.lower():
                            fire_detected = True
                            break
                    if fire_detected:
                        break
                
                if fire_detected:
                    # 计算当前时间点（秒）
                    current_time = int(frame_count / fps)
                    fire_timepoints.append(current_time)
            
            frame_count += 1
        
        cap.release()
        
        return {'duration': duration, 'fire_timepoints': fire_timepoints}
        
    except Exception as e:
        print(f"处理视频时出错: {e}")
        return {'duration': 0, 'fire_timepoints': []}

def cleanup_inactive_sessions():
    try:
        threshold = datetime.utcnow() - timedelta(hours=24)
        inactive_streams = Stream.query.filter(Stream.updated_at < threshold).all()
        
        for stream in inactive_streams:
            if stream.session_id in capturers:
                capturers[stream.session_id].stop()
                del capturers[stream.session_id]
            db.session.delete(stream)
        
        if inactive_streams:
            db.session.commit()
    except Exception as e:
        print(f"清理过期会话时出错: {e}")

@app.route('/export')
@require_login
def export():
    """导出检测结果为Excel文件"""
    try:
        if 'upload_result' not in session:
            return redirect(url_for('upload'))
        
        result = session['upload_result']
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        if result['is_image']:
            writer.writerow(['图片名称', '是否识别到烟火'])
            writer.writerow([result['file_name'], '是' if result['fire_detected'] else '否'])
        else:
            writer.writerow(['视频名称', '时间点（秒）', '是否识别到烟火'])
            duration = result['video_duration']
            fire_timepoints = set(result['fire_timepoints'])
            for second in range(duration + 1):
                writer.writerow([result['file_name'], second, '是' if second in fire_timepoints else '否'])
        
        output.seek(0)
        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename={result["file_name"]}_detection.csv'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bind-logs')
@require_login
def get_bind_logs():
    """获取摄像头绑定日志"""
    try:
        # 检查是否需要获取所有日志
        get_all = request.args.get('all', 'false').lower() == 'true'
        
        # 获取绑定日志，按绑定时间倒序排序
        user_id = session['user_id']
        logs = SystemLog.query.filter_by(user_id=user_id, event_type='camera_bound').order_by(SystemLog.created_at.desc()).all()
        
        # 转换为字典列表
        log_list = []
        for log in logs:
            log_list.append({
                'bind_time': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'camera_name': log.camera_name
            })
        
        # 如果不是获取所有日志，只返回前3条
        if not get_all:
            log_list = log_list[:3]
        
        return jsonify(log_list)
    except Exception as e:
        print(f"获取绑定日志时出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.before_request
def before_request():
    cleanup_inactive_sessions()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # 添加默认预定义摄像头（暂时跳过，避免user_id为NULL的问题）
        # if CameraInfo.query.filter_by(is_predefined=True).count() == 0:
        #     default_cameras = [
        #         {
        #             'name': '办公室USB摄像头',
        #             'source_type': 'usb',
        #             'source_url': '0',
        #             'is_predefined': True
        #         },
        #         {
        #             'name': '仓库网络摄像头',
        #             'source_type': 'rtsp',
        #             'source_url': 'rtsp://admin:123456@192.168.1.100:554/stream',
        #             'ip_address': '192.168.1.100',
        #             'port': 554,
        #             'username': 'admin',
        #             'password': '123456',
        #             'brand': '海康威视',
        #             'model': 'DS-2CD2T45G1-I',
        #             'is_predefined': True
        #         }
        #     ]
        #     
        #     for cam in default_cameras:
        #         camera = CameraInfo(**cam, user_id=None)
        #         db.session.add(camera)
        #     db.session.commit()
    
    app.run(host='0.0.0.0', port=5000, debug=True)