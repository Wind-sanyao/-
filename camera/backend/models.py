from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Stream(db.Model):
    __tablename__ = 'stream'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
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
