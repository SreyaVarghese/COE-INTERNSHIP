from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from attendance_system import start_webcam, capture_frame, update_attendance, end_session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/attendance_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

from models import db, Attendance

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/start_webcam', methods=['POST'])
def start_webcam_route():
    if start_webcam():
        return jsonify({'status': 'success', 'message': 'Webcam started successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to start webcam'})

@app.route('/take_photo', methods=['POST'])
def take_photo():
    frame = capture_frame()
    if frame is not None:
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        return jsonify({'status': 'success', 'message': 'Photo captured successfully', 'frame': frame_bytes.hex()})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to capture photo'})

@app.route('/update_attendance', methods=['POST'])
def update_attendance_route():
    unknown_names, duplicate_names = update_attendance()
    return jsonify({'status': 'success', 'unknown_names': unknown_names, 'duplicate_names': duplicate_names})

@app.route('/take_another_photo', methods=['POST'])
def take_another_photo():
    global captured_frame, recognized_names_global
    captured_frame = None
    recognized_names_global = []
    return jsonify({'status': 'success', 'message': 'Ready to take another photo'})

@app.route('/end_session', methods=['POST'])
def end_session_route():
    result = end_session()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
