from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import cv2
import uuid
from deepface import DeepFace as df
from attendance_system import start_webcam, capture_frame, process_image_file, update_attendance, end_session, recognized_names_global

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
db = SQLAlchemy(app)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Present')

with app.app_context():
    db.create_all()

@app.route('/start_webcam', methods=['GET'])
def start_webcam_route():
    if start_webcam():
        return jsonify({'status': 'success', 'message': 'Webcam started successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to start webcam'}), 500
    
#@app.route('/capture_frame', methods=['GET'])
#def capture_frame_route():
#    annotated_frame, recognized_names = capture_frame()
#    return jsonify({
#        'status': 'success',
#        'annotated_frame': annotated_frame,
#        'recognized_names': recognized_names
#    })

@app.route('/capture_frame', methods=['GET'])
def capture_frame_route():
    annotated_frame = capture_frame()
    if annotated_frame is not None:
        file_path = 'annotated_frame.jpg'
        cv2.imwrite(os.path.join('static/uploads', file_path), annotated_frame)
        return jsonify({'status': 'success', 'file_path': file_path, 'recognized_names': recognized_names_global})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to capture frame'}), 500

@app.route('/upload_image', methods=['POST'])
def upload_image_route():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    if file:
        filename = file.filename
        file_path = os.path.join('static/uploads', filename)
        file.save(file_path)

        annotated_frame, recognized_names = process_image_file(file_path)
        if annotated_frame is not None:
            annotated_path = 'annotated_' + filename
            cv2.imwrite(os.path.join('static/uploads', annotated_path), annotated_frame)
            return jsonify({'status': 'success', 'annotated_image': annotated_path, 'recognized_names': recognized_names})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to process image'}), 500

#@app.route('/upload_image', methods=['POST'])
#def upload_image_route():
#    if 'image' not in request.files:
#        return jsonify({'error': 'No image provided'}), 400
#
#    image_file = request.files['image']
#    if image_file.filename == '':
#        return jsonify({'error': 'No selected file'}), 400
#
#    filename = secure_filename(image_file.filename)
#    file_path = os.path.join('static/uploads', f"{uuid.uuid4()}_{filename}")
#    image_file.save(file_path)
#
#    try:
#        annotated_frame, recognized_names = process_image_file(file_path)
#        return jsonify({'frame': annotated_frame, 'recognized_names': recognized_names}), 200
#    except Exception as e:
#        return jsonify({'error': str(e)}), 500
#

@app.route('/update_attendance', methods=['POST'])
def update_attendance_route():
    try:
        unknown_names, duplicate_names = update_attendance()
        return jsonify({'status': 'success', 'unknown_names': unknown_names, 'duplicate_names': duplicate_names})
    except Exception as e:
        app.logger.error(f'Error updating attendance: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/end_session', methods=['POST'])
def end_session_route():
    try:
        response = end_session()
        return jsonify(response)
    except Exception as e:
        app.logger.error(f'Error ending session: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
