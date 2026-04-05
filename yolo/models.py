from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'phone': self.phone
        }

class CameraInfo(db.Model):
    __tablename__ = 'camera_info'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String(50), nullable=False)
    source_type = db.Column(db.String(10), nullable=False)
    source_url = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(50))
    port = db.Column(db.Integer)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    is_predefined = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'source_type': self.source_type,
            'source_url': self.source_url,
            'ip_address': self.ip_address,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'brand': self.brand,
            'model': self.model,
            'is_predefined': self.is_predefined
        }

class Stream(db.Model):
    __tablename__ = 'stream'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    source_type = db.Column(db.String(10), nullable=False)
    source_url = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='connecting')
    error_info = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'source_type': self.source_type,
            'name': self.name,
            'status': self.status,
            'error': self.error_info,
            'timestamp': int(self.updated_at.timestamp())
        }

class SystemLog(db.Model):
    __tablename__ = 'system_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    camera_name = db.Column(db.String(50), nullable=False)
    event_type = db.Column(db.String(20), nullable=False)  # fire_detected, camera_bound
    event_message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'camera_name': self.camera_name,
            'event_type': self.event_type,
            'event_message': self.event_message,
            'created_at': self.created_at.isoformat()
        }

class UserSetting(db.Model):
    __tablename__ = 'user_setting'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    theme = db.Column(db.String(20), default='light')  # light, dark
    font_size = db.Column(db.String(20), default='medium')  # small, medium, large
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'theme': self.theme,
            'font_size': self.font_size
        }