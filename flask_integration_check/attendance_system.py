from deepface import DeepFace as df
import cv2
import os
from datetime import datetime, timedelta
from models import db, Attendance

known_faces_dir = 'data_and_installs/aug_images'
cap = None  # Global variable for the webcam
captured_frame = None  # Global variable for the captured frame
recognized_names_global = []  # Global variable for recognized names
duplicate_names_set = set()

def start_webcam():
    global cap
    cap = cv2.VideoCapture(0)
    return cap.isOpened()

def capture_frame():
    global captured_frame, recognized_names_global, duplicate_names_set
    success, frame = cap.read()
    if success:
        captured_frame = frame
        face_bboxes, recognized_names = recognize_faces2(frame, known_faces_dir)
        recognized_names_global = recognized_names
        annotated_frame = annotate_frame(frame, face_bboxes, recognized_names)
        return annotated_frame
    else:
        return None

def recognize_faces2(frame, dir):
    face_bboxes = []
    recognized_names = []

    matches = df.find(img_path=frame, db_path=dir, model_name='Facenet512',
                      distance_metric='cosine', enforce_detection=False, detector_backend='retinaface',
                      align=True, expand_percentage=5, threshold=3)
    if matches and len(matches) > 0:
        for i in range(len(matches)):
            name = 'UNKNOWN'
            dataframe = matches[i]
            min_dis_row = dataframe.loc[dataframe['distance'].idxmin()]
            if min_dis_row['distance'] <= 0.4:
                min_dis_img_path = min_dis_row['identity']
                base = os.path.basename(min_dis_img_path)
                face_name = os.path.splitext(base)[0]
                name = ''.join(filter(lambda x: not x.isdigit(), face_name)).strip()

            face_loc = [dataframe['source_x'][0], dataframe['source_y'][0], dataframe['source_w'][0], dataframe['source_h'][0]]
            face_bboxes.append(face_loc)
            recognized_names.append(name)
    return face_bboxes, recognized_names

def annotate_frame(frame, face_bboxes, recognized_names):
    global recognized_names_global, duplicate_names_set

    duplicate_names_set = set()
    names_set = set(recognized_names_global)

    for loc, name in zip(face_bboxes, recognized_names):
        x, y, w, h = loc
        if name in names_set:
            duplicate_names_set.add(name)
        names_set.add(name)

        box_color = (0, 255, 0) if name != 'UNKNOWN' else (0, 0, 255)
        thick = 2 if name != 'UNKNOWN' else 3
        font_color = (0, 0, 255) if name != 'UNKNOWN' else (0, 100, 255)

        if name in duplicate_names_set:
            box_color = (0, 0, 0)
            font_color = (0, 255, 0)

        cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, thick)
        cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, font_color, 1)

    return frame

def update_attendance():
    current_time = datetime.now()
    attendance_dict = {}
    unknown_names = 0

    # Fetch existing attendance records
    existing_attendance = Attendance.query.all()
    for record in existing_attendance:
        attendance_dict[record.name] = record.timestamp

    for name in recognized_names_global:
        if name != 'UNKNOWN':
            if name in attendance_dict:
                last_attendance_time = attendance_dict[name]
                time_diff = current_time - last_attendance_time
                if time_diff >= timedelta(minutes=30):  # Adjust timedelta threshold as needed
                    attendance = Attendance(name=name, timestamp=current_time, status='Present')
                    db.session.add(attendance)
                    attendance_dict[name] = current_time
            else:
                attendance = Attendance(name=name, timestamp=current_time, status='Present')
                db.session.add(attendance)
        else:
            unknown_names += 1
    
    db.session.commit()
    return unknown_names, list(duplicate_names_set)

def end_session():
    global cap
    if cap:
        cap.release()
    cv2.destroyAllWindows()
    return {'status': 'success'}
