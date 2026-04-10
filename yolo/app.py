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
        
        # 先尝试通过手机号查找用户
        user = User.query.filter_by(phone=phone).first()
        # 如果没找到，尝试通过用户名查找
        if not user:
            user = User.query.filter_by(username=phone).first()
        
        if user and user.password == hash_password(password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        return render_template('login.html', error='用户名或手机号或密码错误')
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
            is_image = file_ext in ['.jpg', '.jpeg', '.png']
            is_gif = file_ext == '.gif'
            is_video = file_ext in ['.mp4', '.avi', '.mov', '.wmv']
            
            if not (is_image or is_gif or is_video):
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
            elif is_gif:
                # 处理GIF
                result = process_gif(file_path)
            else:
                # 处理视频
                result = process_video(file_path)
            
            # 构建响应
            if is_gif:
                response = {
                    'success': True,
                    'file_name': file.filename,
                    'file_type': 'GIF动画',
                    'file_size': f"{os.path.getsize(file_path) / 1024:.2f} KB",
                    'is_gif': True,
                    'gif_duration': result['duration'],
                    'fire_timepoints': result['fire_timepoints'],
                    'fire_detected': result['fire_detected'],
                    'annotated_gif': result.get('annotated_gif')
                }
            elif is_video:
                response = {
                    'success': True,
                    'file_name': file.filename,
                    'file_type': '视频',
                    'file_size': f"{os.path.getsize(file_path) / 1024:.2f} KB",
                    'is_video': True,
                    'video_duration': result['duration'],
                    'fire_timepoints': result['fire_timepoints'],
                    'fire_detected': result['fire_detected'],
                    'annotated_video': result.get('annotated_video')
                }
            else:
                response = {
                    'success': True,
                    'file_name': file.filename,
                    'file_type': '图片',
                    'file_size': f"{os.path.getsize(file_path) / 1024:.2f} KB",
                    'is_image': True,
                    'results': result
                }
            
            if is_image:
                response['fire_detected'] = result['fire_detected']
                response['confidence'] = result['confidence']
                # 使用带有检测标记的图片
                if result.get('annotated_image'):
                    response['image_data'] = result['annotated_image']
                else:
                    # 如果没有标记图片，使用原始图片
                    with open(file_path, 'rb') as f:
                        import base64
                        response['image_data'] = base64.b64encode(f.read()).decode('utf-8')
            elif is_gif:
                # GIF已在process_gif中处理
                pass
            elif is_video:
                # 视频已在process_video中处理
                pass
            
            # 保存到会话，用于导出（不包含base64编码）
            session['upload_result'] = {
                'file_name': file.filename,
                'file_type': '图片' if is_image else '视频',
                'is_image': is_image,
                'fire_detected': result.get('fire_detected', False),
                'confidence': result.get('confidence', 0.0),
                'video_duration': result.get('duration', 0),
                'fire_timepoints': result.get('fire_timepoints', [])
            }
            
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
    
    # 获取用户的摄像头列表
    user_cameras = CameraInfo.query.filter_by(user_id=user_id).all()
    
    if request.method == 'POST':
        theme = request.form['theme']
        font_size = request.form['font_size']
        
        setting.theme = theme
        setting.font_size = font_size
        db.session.commit()
        return render_template('settings.html', user=user, setting=setting, user_cameras=user_cameras, message='设置已保存')
    
    return render_template('settings.html', user=user, setting=setting, user_cameras=user_cameras)

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
        
        # 创建或获取CameraInfo记录
        camera = CameraInfo(
            user_id=user_id,
            name=name,
            source_type=camera_type,
            source_url=source_url,
            is_predefined=False
        )
        db.session.add(camera)
        db.session.commit()
        
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
        
        capturer = VideoCapturer(camera_type, source_url, user_id, camera.id)
        print(f"创建VideoCapturer实例: {camera_type}, {source_url}, {user_id}, camera_id: {camera.id}")
        
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
        
        session_id = str(uuid.uuid4())
        source_url = ''
        camera_type = None
        name = None
        
        # 处理选择已有摄像头的情况
        if 'cameraId' in data:
            camera_id = data.get('cameraId')
            camera = CameraInfo.query.filter_by(id=int(camera_id)).first()
            if not camera:
                return jsonify({'success': False, 'error': '所选摄像头不存在'}), 404
            
            camera_type = camera.source_type
            name = camera.name
            
            if camera_type == 'usb':
                source_url = camera.source_url or '0'
            elif camera_type == 'rtsp':
                # 从摄像头信息中构建RTSP URL
                if camera.ip_address and camera.username and camera.password:
                    port = camera.port or 554
                    source_url = f'rtsp://{camera.username}:{camera.password}@{camera.ip_address}:{port}/stream'
                else:
                    return jsonify({'success': False, 'error': '网络摄像头信息不完整'}), 400
        # 处理绑定新摄像头的情况
        else:
            camera_type = data.get('cameraType')
            name = data.get('name')
            
            if not camera_type or not name:
                return jsonify({'success': False, 'error': '缺少必要参数'}), 400
            
            if len(name) > 50:
                return jsonify({'success': False, 'error': '摄像头名称不能超过50个字符'}), 400
            
            if camera_type == 'usb':
                device_index = data.get('deviceIndex', 0)
                source_url = str(device_index)
            elif camera_type == 'rtsp':
                ip = data.get('ipAddress')
                port = data.get('port', 554)
                username = data.get('username')
                password = data.get('password')
                brand = data.get('brand', '')
                
                if not ip or not username or not password:
                    return jsonify({'success': False, 'error': '网络摄像头信息不完整'}), 400
                
                # 根据摄像头品牌构建不同的RTSP URL格式
                if brand == 'hikvision':
                    # 海康威视RTSP URL格式
                    source_url = f'rtsp://{username}:{password}@{ip}:{port}/h264/ch1/main/av_stream'
                elif brand == 'dahua':
                    # 大华RTSP URL格式
                    source_url = f'rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel=1&subtype=0'
                elif brand == 'axis':
                    # 安讯士RTSP URL格式
                    source_url = f'rtsp://{username}:{password}@{ip}:{port}/axis-media/media.amp'
                else:
                    # 默认RTSP URL格式
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
        
        # 尝试从capturer获取检测画面
        if session_id in capturers:
            capturer = capturers[session_id]
            frame_data = capturer.get_detected_frame()
            if frame_data:
                # 更新stream时间
                if stream:
                    stream.updated_at = datetime.utcnow()
                    db.session.commit()
                
                response = Response(frame_data, mimetype='image/jpeg')
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
        
        # 如果无法获取检测画面，创建一个默认帧
        try:
            import cv2
            import numpy as np
            # 创建一个黑色背景的默认帧
            black_frame = cv2.zeros((480, 640, 3), dtype=np.uint8)
            ret, jpeg = cv2.imencode('.jpg', black_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if ret:
                frame_data = jpeg.tobytes()
                
                # 更新stream时间
                if stream:
                    stream.updated_at = datetime.utcnow()
                    db.session.commit()
                
                response = Response(frame_data, mimetype='image/jpeg')
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
        except Exception as e:
            print(f"创建默认帧失败: {e}")
        
        # 如果创建默认帧失败，返回一个简单的黑色帧
        # 创建一个最小的黑色JPEG图像
        import base64
        # 这是一个1x1的黑色JPEG图像的base64编码
        black_jpeg = base64.b64decode('Qk02AAAAAAAAABsAAAAIAAAASAAAABwAAAAMAAAABAAEAAAAAfgAAAB8AAAAgAAAAJAEAAAEBwYF//8A')
        response = Response(black_jpeg, mimetype='image/jpeg')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
            
    except Exception as e:
        print(f"获取检测画面出错: {e}")
        # 即使出现异常，也返回一个最小的黑色JPEG图像
        import base64
        black_jpeg = base64.b64decode('Qk02AAAAAAAAABsAAAAIAAAASAAAABwAAAAMAAAABAAEAAAAAfgAAAB8AAAAgAAAAJAEAAAEBwYF//8A')
        response = Response(black_jpeg, mimetype='image/jpeg')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

@app.route('/api/camera/detection/status/<session_id>')
@require_login
def get_detection_status(session_id):
    try:
        user_id = session['user_id']
        stream = Stream.query.filter_by(session_id=session_id, user_id=user_id).first()
        
        if not stream:
            return jsonify({'error': '会话不存在'}), 404
        
        if stream.status != 'connected':
            # 如果状态不是connected，返回默认状态
            return jsonify({
                'fire_detected': False,
                'confidence': 0.0,
                'last_detection_time': None
            })
        
        if session_id not in capturers:
            # 如果session_id不在capturers字典中，返回默认状态
            return jsonify({
                'fire_detected': False,
                'confidence': 0.0,
                'last_detection_time': None
            })
        
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

@app.route('/api/camera/test', methods=['POST'])
@require_login
def test_camera():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400
        
        device_index = data.get('deviceIndex', 0)
        
        import cv2
        cap = cv2.VideoCapture(int(device_index))
        
        if cap.isOpened():
            # 尝试读取一帧
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return jsonify({'success': True, 'message': '摄像头测试成功'})
            else:
                return jsonify({'success': False, 'error': '摄像头打开成功，但无法读取画面'}), 500
        else:
            cap.release()
            return jsonify({'success': False, 'error': f'无法打开摄像头，设备索引: {device_index}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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

from models import FireDetection

# 全局模型缓存，避免重复加载
_image_model = None

def get_image_model():
    """获取或加载图片检测模型"""
    global _image_model
    if _image_model is None:
        try:
            from ultralytics import YOLO
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, 'runs', 'detect_v2', 'weights', 'best.pt')
            
            print(f"Loading model from: {model_path}")
            if os.path.exists(model_path):
                _image_model = YOLO(model_path)
                print(f"Model loaded successfully")
            else:
                print(f"Model not found at: {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()
    return _image_model

def process_image(file_path):
    """处理图片，检测是否有烟火，并返回标记后的图片"""
    try:
        import cv2
        import base64
        
        print(f"Processing image: {file_path}")
        
        # 加载模型
        model = get_image_model()
        if model is None:
            print("Model not loaded, returning default result")
            return {'fire_detected': False, 'confidence': 0.0, 'annotated_image': None}
        
        # 读取图片
        img = cv2.imread(file_path)
        if img is None:
            print(f"Failed to read image: {file_path}")
            return {'fire_detected': False, 'confidence': 0.0, 'annotated_image': None}
        
        print(f"Image loaded successfully, shape: {img.shape}")
        
        # 检测
        results = model(img, conf=0.5, verbose=False)
        print(f"Detection completed, results count: {len(results)}")
        
        fire_detected = False
        max_confidence = 0.0
        detected_classes = []
        
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names[class_id]
                detected_classes.append(f"{class_name} ({confidence:.2f})")
                
                print(f"Detected: {class_name} with confidence {confidence}")
                
                if 'fire' in class_name.lower() or 'smoke' in class_name.lower():
                    fire_detected = True
                    if confidence > max_confidence:
                        max_confidence = confidence
        
        print(f"Final result: fire_detected={fire_detected}, confidence={max_confidence}")
        print(f"All detected classes: {detected_classes}")
        
        # 生成带有检测标记的图片
        annotated_image = None
        if len(results) > 0:
            # 使用YOLO的plot方法绘制检测框
            annotated_frame = results[0].plot()
            # 将图片转换为base64
            ret, jpeg = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            if ret:
                annotated_image = base64.b64encode(jpeg.tobytes()).decode('utf-8')
        
        return {'fire_detected': fire_detected, 'confidence': max_confidence, 'annotated_image': annotated_image}
        
    except Exception as e:
        print(f"处理图片时出错: {e}")
        import traceback
        traceback.print_exc()
        return {'fire_detected': False, 'confidence': 0.0, 'annotated_image': None}

def process_gif(file_path):
    """处理GIF动画，检测是否有烟火"""
    try:
        import cv2
        import base64
        from PIL import Image
        import io
        
        print(f"Processing GIF: {file_path}")
        
        # 加载模型
        model = get_image_model()
        if model is None:
            print("Model not loaded, returning default result")
            return {'duration': 0, 'fire_timepoints': [], 'fire_detected': False, 'annotated_gif': None}
        
        # 打开GIF文件
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print(f"Failed to open GIF: {file_path}")
            return {'duration': 0, 'fire_timepoints': [], 'fire_detected': False, 'annotated_gif': None}
        
        # 获取GIF信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = int(total_frames / fps) if fps > 0 else 0
        
        print(f"GIF info: {total_frames} frames, {fps} fps, {duration}s duration")
        
        fire_timepoints = []
        annotated_frames = []
        frame_count = 0
        fire_detected = False
        
        # 每3帧检测一帧（GIF通常帧率较低）
        sample_interval = max(1, int(fps / 3)) if fps > 0 else 3
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 采样检测
            if frame_count % sample_interval == 0:
                # 检测
                results = model(frame, conf=0.5, verbose=False)
                
                frame_fire_detected = False
                for result in results:
                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        class_name = model.names[class_id]
                        
                        if 'fire' in class_name.lower() or 'smoke' in class_name.lower():
                            frame_fire_detected = True
                            fire_detected = True
                            break
                    if frame_fire_detected:
                        break
                
                if frame_fire_detected:
                    # 计算当前时间点（秒）
                    current_time = int(frame_count / fps) if fps > 0 else frame_count
                    if current_time not in fire_timepoints:
                        fire_timepoints.append(current_time)
                
                # 生成带有检测标记的帧
                if len(results) > 0:
                    annotated_frame = results[0].plot()
                    annotated_frames.append(annotated_frame)
                else:
                    annotated_frames.append(frame)
            else:
                # 使用原始帧
                annotated_frames.append(frame)
            
            frame_count += 1
        
        cap.release()
        
        print(f"GIF processing completed: {len(fire_timepoints)} fire detections")
        
        # 生成标记后的GIF（只取前30帧，避免文件过大）
        annotated_gif = None
        if annotated_frames:
            try:
                # 限制帧数，避免文件过大
                max_frames = min(30, len(annotated_frames))
                sample_frames = annotated_frames[::max(1, len(annotated_frames) // max_frames)][:max_frames]
                
                # 将OpenCV帧转换为PIL图像
                pil_frames = []
                for frame in sample_frames:
                    # OpenCV使用BGR，PIL使用RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(rgb_frame)
                    # 等比缩放，最大宽度600像素
                    max_width = 600
                    if pil_image.width > max_width:
                        ratio = max_width / pil_image.width
                        new_height = int(pil_image.height * ratio)
                        pil_image = pil_image.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    pil_frames.append(pil_image)
                
                # 保存为GIF
                if pil_frames:
                    gif_buffer = io.BytesIO()
                    pil_frames[0].save(
                        gif_buffer,
                        format='GIF',
                        save_all=True,
                        append_images=pil_frames[1:],
                        duration=100,  # 每帧100ms
                        loop=0
                    )
                    gif_buffer.seek(0)
                    annotated_gif = base64.b64encode(gif_buffer.getvalue()).decode('utf-8')
                    print(f"Annotated GIF generated: {len(annotated_gif)} bytes")
            except Exception as e:
                print(f"Error generating annotated GIF: {e}")
                import traceback
                traceback.print_exc()
        
        return {
            'duration': duration,
            'fire_timepoints': fire_timepoints,
            'fire_detected': fire_detected,
            'annotated_gif': annotated_gif
        }
        
    except Exception as e:
        print(f"处理GIF时出错: {e}")
        import traceback
        traceback.print_exc()
        return {'duration': 0, 'fire_timepoints': [], 'fire_detected': False, 'annotated_gif': None}

def process_video(file_path):
    """处理视频，检测是否有烟火"""
    try:
        import cv2
        from ultralytics import YOLO
        import base64
        import io
        
        # 加载模型
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'runs', 'detect_v2', 'weights', 'best.pt')
        
        if os.path.exists(model_path):
            model = YOLO(model_path)
        else:
            # 如果模型不存在，返回默认结果
            return {'duration': 0, 'fire_timepoints': [], 'fire_detected': False, 'annotated_video': None}
        
        # 打开视频
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return {'duration': 0, 'fire_timepoints': [], 'fire_detected': False, 'annotated_video': None}
        
        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = int(total_frames / fps) if fps > 0 else 0
        
        fire_timepoints = []
        frame_count = 0
        fire_detected = False
        annotated_frames = []
        
        # 限制处理的帧数，避免文件过大
        max_frames = 30
        frame_interval = max(1, int(total_frames / max_frames))
        
        # 处理视频帧
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 每隔一定帧数处理一帧
            if frame_count % frame_interval == 0:
                # 检测
                results = model(frame, conf=0.5, verbose=False)
                
                frame_fire_detected = False
                for result in results:
                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        class_name = model.names[class_id]
                        
                        if 'fire' in class_name.lower() or 'smoke' in class_name.lower():
                            frame_fire_detected = True
                            fire_detected = True
                            break
                    if frame_fire_detected:
                        break
                
                if frame_fire_detected:
                    # 计算当前时间点（秒）
                    current_time = int(frame_count / fps)
                    if current_time not in fire_timepoints:
                        fire_timepoints.append(current_time)
                
                # 生成带有检测标记的帧
                if len(results) > 0:
                    annotated_frame = results[0].plot()
                    # 等比缩放，最大宽度600像素
                    max_width = 600
                    if annotated_frame.shape[1] > max_width:
                        ratio = max_width / annotated_frame.shape[1]
                        new_height = int(annotated_frame.shape[0] * ratio)
                        annotated_frame = cv2.resize(annotated_frame, (max_width, new_height))
                    annotated_frames.append(annotated_frame)
                else:
                    # 等比缩放，最大宽度600像素
                    max_width = 600
                    if frame.shape[1] > max_width:
                        ratio = max_width / frame.shape[1]
                        new_height = int(frame.shape[0] * ratio)
                        frame = cv2.resize(frame, (max_width, new_height))
                    annotated_frames.append(frame)
            
            frame_count += 1
        
        cap.release()
        
        # 生成标记后的视频（转换为GIF格式以便在网页上显示）
        annotated_video = None
        if annotated_frames:
            try:
                from PIL import Image
                
                # 将OpenCV帧转换为PIL图像
                pil_frames = []
                for frame in annotated_frames:
                    # OpenCV使用BGR，PIL使用RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(rgb_frame)
                    pil_frames.append(pil_image)
                
                # 保存为GIF
                if pil_frames:
                    gif_buffer = io.BytesIO()
                    pil_frames[0].save(
                        gif_buffer,
                        format='GIF',
                        save_all=True,
                        append_images=pil_frames[1:],
                        duration=100,  # 每帧100ms
                        loop=0
                    )
                    gif_buffer.seek(0)
                    annotated_video = base64.b64encode(gif_buffer.getvalue()).decode('utf-8')
                    print(f"Annotated video generated: {len(annotated_video)} bytes")
            except Exception as e:
                print(f"Error generating annotated video: {e}")
                import traceback
                traceback.print_exc()
        
        return {
            'duration': duration,
            'fire_timepoints': fire_timepoints,
            'fire_detected': fire_detected,
            'annotated_video': annotated_video
        }
        
    except Exception as e:
        print(f"处理视频时出错: {e}")
        import traceback
        traceback.print_exc()
        return {'duration': 0, 'fire_timepoints': [], 'fire_detected': False, 'annotated_video': None}

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

@app.route('/upload/folder', methods=['GET', 'POST'])
@require_login
def upload_folder():
    """处理文件夹上传"""
    user_id = session['user_id']
    user = User.query.get(user_id)
    setting = UserSetting.query.filter_by(user_id=user_id).first()
    
    if request.method == 'POST':
        try:
            # 检查是否有文件上传
            if 'files' not in request.files:
                return jsonify({'success': False, 'error': '请选择文件夹'})
            
            files = request.files.getlist('files')
            
            if not files:
                return jsonify({'success': False, 'error': '请选择文件夹'})
            
            # 保存文件
            upload_dir = os.path.join(BASE_DIR, 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            fire_detected_count = 0
            fire_files = []
            
            for file in files:
                # 检查文件类型
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                    continue
                
                file_path = os.path.join(upload_dir, file.filename)
                file.save(file_path)
                
                # 处理图片
                result = process_image(file_path)
                if result['fire_detected']:
                    fire_detected_count += 1
                    fire_files.append(file.filename)
            
            # 构建响应
            response = {
                'success': True,
                'files_count': len(files),
                'fire_detected_count': fire_detected_count,
                'fire_files': fire_files,
                'is_folder': True
            }
            
            # 保存到会话，用于导出
            session['upload_result'] = {
                'files_count': len(files),
                'fire_detected_count': fire_detected_count,
                'fire_files': fire_files[:10],  # 限制保存的文件数量，避免会话过大
                'is_folder': True
            }
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return render_template('upload.html', user=user, setting=setting)

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
        elif result.get('is_folder'):
            writer.writerow(['文件夹检测结果'])
            writer.writerow(['处理文件数', result['files_count']])
            writer.writerow(['检测到烟火的文件数', result['fire_detected_count']])
            if result.get('fire_files'):
                writer.writerow(['检测到烟火的文件'])
                for file in result['fire_files']:
                    writer.writerow([file])
        else:
            writer.writerow(['视频名称', '时间点（秒）', '是否识别到烟火'])
            duration = result['video_duration']
            fire_timepoints = set(result['fire_timepoints'])
            for second in range(duration + 1):
                writer.writerow([result['file_name'], second, '是' if second in fire_timepoints else '否'])
        
        output.seek(0)
        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename=folder_detection.csv'
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

@app.route('/api/detection/export', methods=['POST'])
@require_login
def export_detection_data():
    """导出摄像头检测数据为Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        from datetime import datetime
        
        user_id = session['user_id']
        camera_id = request.form.get('camera_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        start_time = request.form.get('start_time', '00:00')
        end_time = request.form.get('end_time', '23:59')
        
        # 检查摄像头是否存在且启用过
        if camera_id and camera_id != '':
            camera = CameraInfo.query.filter_by(id=int(camera_id), user_id=user_id).first()
            if not camera:
                return jsonify({'success': False, 'error': '选择的摄像头不存在'})
            
            # 检查摄像头是否启用过（是否有检测数据）
            has_detection = FireDetection.query.filter_by(camera_id=int(camera_id), user_id=user_id).first()
            if not has_detection:
                return jsonify({'success': False, 'error': '选择的摄像头未启用过，没有检测数据'})
        
        # 构建查询
        query = FireDetection.query.filter_by(user_id=user_id)
        
        # 按摄像头过滤
        if camera_id and camera_id != '':
            query = query.filter_by(camera_id=int(camera_id))
        
        # 按日期过滤
        if start_date:
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
            query = query.filter(FireDetection.detected_at >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
            query = query.filter(FireDetection.detected_at <= end_datetime)
        
        # 执行查询
        detections = query.order_by(FireDetection.detected_at).all()
        
        if not detections:
            return jsonify({'success': False, 'error': '所选时间段内没有检测数据'})
        
        # 转换为DataFrame，只包含检测到烟火的时间和相关信息
        data = []
        for detection in detections:
            data.append({
                '检测时间': detection.detected_at,
                '摄像头名称': detection.camera_name,
                '检测状态': '火灾' if detection.status == 'fire' else '烟雾',
                '置信度': f"{detection.confidence * 100:.2f}%"
            })
        
        df = pd.DataFrame(data)
        
        # 生成Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='检测数据', index=False)
        output.seek(0)
        
        return send_file(output, download_name=f'摄像头检测数据_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx', as_attachment=True)
        
    except Exception as e:
        print(f"导出检测数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

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