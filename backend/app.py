import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from models import db, CalibrateRecord, LeaveRecord, ModifyLog

app = Flask(__name__, static_folder='../')
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'duty.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '316-duty-secret-key'

CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

db.init_app(app)

with app.app_context():
    db.create_all()

VALID_NAMES = ['夏蒋全', '黄诗颖', '宋子慧', '方圆圆', '朱晨依']
ADMIN_NAME = '夏蒋全'

@app.route('/')
def index():
    return send_from_directory('../', 'index.html')

@app.route('/api/verify', methods=['POST'])
def verify_name():
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if name in VALID_NAMES:
        return jsonify({
            'success': True,
            'name': name,
            'isAdmin': name == ADMIN_NAME
        })
    return jsonify({
        'success': False,
        'message': '姓名不在名单中'
    }), 400

@app.route('/api/records', methods=['GET'])
def get_records():
    calibrate_records = {}
    for record in CalibrateRecord.query.all():
        calibrate_records[record.date] = record.data
    
    leave_records = {}
    for record in LeaveRecord.query.all():
        leave_records[record.date] = {
            'leaver': record.leaver,
            'substitute': record.substitute,
            'promiseDate': record.promise_date
        }
    
    return jsonify({
        'success': True,
        'calibrateRecords': calibrate_records,
        'leaveRecords': leave_records
    })

@app.route('/api/calibrate', methods=['POST'])
def save_calibrate():
    data = request.get_json()
    date = data.get('date')
    calibration = data.get('calibration')
    operator = data.get('operator')
    
    if operator != ADMIN_NAME:
        return jsonify({'success': False, 'message': '只有管理员可以校准'}), 403
    
    existing = CalibrateRecord.query.filter_by(date=date).first()
    before_data = existing.data if existing else None
    
    if existing:
        existing.data = calibration
        existing.updated_by = operator
    else:
        record = CalibrateRecord(date=date, data=calibration, updated_by=operator)
        db.session.add(record)
    
    log = ModifyLog(
        action='calibrate',
        date=date,
        operator=operator,
        before_data=before_data,
        after_data=calibration,
        detail=f'校准日期 {date}'
    )
    db.session.add(log)
    db.session.commit()
    
    socketio.emit('data_updated', {'type': 'calibrate', 'date': date})
    
    return jsonify({'success': True})

@app.route('/api/leave', methods=['POST'])
def save_leave():
    data = request.get_json()
    date = data.get('date')
    leaver = data.get('leaver')
    substitute = data.get('substitute')
    promise_date = data.get('promiseDate')
    operator = data.get('operator')
    
    existing = LeaveRecord.query.filter_by(date=date).first()
    before_data = None
    if existing:
        before_data = {
            'leaver': existing.leaver,
            'substitute': existing.substitute,
            'promiseDate': existing.promise_date
        }
    
    if existing:
        existing.leaver = leaver
        existing.substitute = substitute
        existing.promise_date = promise_date
        existing.updated_by = operator
    else:
        record = LeaveRecord(
            date=date,
            leaver=leaver,
            substitute=substitute,
            promise_date=promise_date,
            updated_by=operator
        )
        db.session.add(record)
    
    log = ModifyLog(
        action='leave',
        date=date,
        operator=operator,
        before_data=before_data,
        after_data={'leaver': leaver, 'substitute': substitute, 'promiseDate': promise_date},
        detail=f'{leaver} 请假，{substitute} 代班'
    )
    db.session.add(log)
    db.session.commit()
    
    socketio.emit('data_updated', {'type': 'leave', 'date': date})
    
    return jsonify({'success': True})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    logs = ModifyLog.query.order_by(ModifyLog.timestamp.desc()).limit(50).all()
    return jsonify({
        'success': True,
        'logs': [{
            'id': log.id,
            'action': log.action,
            'date': log.date,
            'operator': log.operator,
            'beforeData': log.before_data,
            'afterData': log.after_data,
            'detail': log.detail,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for log in logs]
    })

@app.route('/api/rollback/<int:log_id>', methods=['POST'])
def rollback(log_id):
    data = request.get_json()
    operator = data.get('operator')
    
    if operator != ADMIN_NAME:
        return jsonify({'success': False, 'message': '只有管理员可以回滚'}), 403
    
    log = ModifyLog.query.get(log_id)
    if not log:
        return jsonify({'success': False, 'message': '日志不存在'}), 404
    
    if log.action == 'calibrate':
        if log.before_data is None:
            CalibrateRecord.query.filter_by(date=log.date).delete()
        else:
            record = CalibrateRecord.query.filter_by(date=log.date).first()
            if record:
                record.data = log.before_data
            else:
                record = CalibrateRecord(date=log.date, data=log.before_data)
                db.session.add(record)
    
    elif log.action == 'leave':
        if log.before_data is None:
            LeaveRecord.query.filter_by(date=log.date).delete()
        else:
            record = LeaveRecord.query.filter_by(date=log.date).first()
            if record:
                record.leaver = log.before_data['leaver']
                record.substitute = log.before_data['substitute']
                record.promise_date = log.before_data.get('promiseDate')
            else:
                record = LeaveRecord(
                    date=log.date,
                    leaver=log.before_data['leaver'],
                    substitute=log.before_data['substitute'],
                    promise_date=log.before_data.get('promiseDate')
                )
                db.session.add(record)
    
    rollback_log = ModifyLog(
        action='rollback',
        date=log.date,
        operator=operator,
        before_data=log.after_data,
        after_data=log.before_data,
        detail=f'回滚操作 #{log_id}'
    )
    db.session.add(rollback_log)
    db.session.commit()
    
    socketio.emit('data_updated', {'type': 'rollback', 'date': log.date})
    
    return jsonify({'success': True})

@app.route('/api/clear/leave', methods=['POST'])
def clear_leave():
    data = request.get_json()
    operator = data.get('operator')
    
    LeaveRecord.query.delete()
    
    log = ModifyLog(
        action='clear_leave',
        operator=operator,
        detail='清除所有调班记录'
    )
    db.session.add(log)
    db.session.commit()
    
    socketio.emit('data_updated', {'type': 'clear_leave'})
    
    return jsonify({'success': True})

@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': '连接成功'})

@socketio.on('disconnect')
def handle_disconnect():
    print('客户端断开连接')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
