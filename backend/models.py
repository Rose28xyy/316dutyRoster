from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class CalibrateRecord(db.Model):
    __tablename__ = 'calibrate_records'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), unique=True, nullable=False)
    data = db.Column(db.JSON, nullable=False)
    updated_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LeaveRecord(db.Model):
    __tablename__ = 'leave_records'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), unique=True, nullable=False)
    leaver = db.Column(db.String(50), nullable=False)
    substitute = db.Column(db.String(50), nullable=False)
    promise_date = db.Column(db.String(20))
    updated_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ModifyLog(db.Model):
    __tablename__ = 'modify_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20))
    operator = db.Column(db.String(50), nullable=False)
    before_data = db.Column(db.JSON)
    after_data = db.Column(db.JSON)
    detail = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
