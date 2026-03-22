from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
import os
import random
from models import db, Stream
from camera import VideoCapturer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///camera.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

capturers = {}

@app.route('/')
def index():
    return render_template('bind.html')

@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

@app.route('/api/camera/bind', methods=['POST'])
def bind_camera():
    try:
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
            source_type=camera_type,
            source_url=source_url,
            name=name,
            status='connecting'
        )
        db.session.add(stream)
        db.session.commit()
        
        capturer = VideoCapturer(camera_type, source_url)
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
            return jsonify({'success': False, 'error': stream.error_info or '无法连接摄像头，请检查设备是否正常'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/camera/snapshot/<session_id>')
def get_snapshot(session_id):
    try:
        stream = Stream.query.filter_by(session_id=session_id).first()
        
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

@app.route('/api/camera/info/<session_id>')
def get_camera_info(session_id):
    try:
        stream = Stream.query.filter_by(session_id=session_id).first()
        
        if not stream:
            return jsonify({'error': '会话不存在'}), 404
        
        return jsonify(stream.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/unbind/<session_id>', methods=['DELETE'])
def unbind_camera(session_id):
    try:
        stream = Stream.query.filter_by(session_id=session_id).first()
        
        if stream:
            db.session.delete(stream)
            db.session.commit()
        
        if session_id in capturers:
            capturers[session_id].stop()
            del capturers[session_id]
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def cleanup_inactive_sessions():
    try:
        if random.random() > 0.01:
            return
        
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

@app.before_request
def before_request():
    cleanup_inactive_sessions()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
