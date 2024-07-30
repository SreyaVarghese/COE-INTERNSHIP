from deepface import DeepFace as df
import cv2,csv
import os
import numpy as np
from datetime import datetime, timedelta
from models import db, Attendance

known_faces_dir = 'data_and_installs/aug_images'
cap = None  # Global variable for the webcam
recognized_names_global = []  # Global variable for recognized names
duplicate_names_set = set()

def start_webcam():
    global cap
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("Session Started successfully!")
        return True
    else:
        print("Failed to start session!")
        return False

def capture_frame():
    global recognized_names_global, duplicate_names_set
    if cap is None or not cap.isOpened():
        print("Webcam is not initialized or opened")
        return None

    success, frame = cap.read()
    #frame=cv2.resize(frame,(950,600))
    print(f"Frame capture success: {success}")
    if success:
        if frame is None or frame.size == 0:
            print("Captured frame is empty")
            return None
        face_bboxes, recognized_names = recognize_faces2(frame, known_faces_dir)
        print(f"Recognized names: {recognized_names}")
        recognized_names_global = recognized_names
        annotated_frame = annotate_frame(frame, face_bboxes, recognized_names)
        return annotated_frame
    else:
        print("Failed to capture frame")
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
 


#def recognize_faces2(frame, dir):
#    face_bboxes = []
#    recognized_names = []
#
#    matches = df.find(img_path=frame, db_path=dir, model_name='Facenet512',
#                      distance_metric='cosine', enforce_detection=False, detector_backend='retinaface',
#                      align=True, expand_percentage=5, threshold=0.4)
#    if matches and len(matches) > 0:
#        for match in matches:
#            name = 'UNKNOWN'
#            min_dis_row = match.loc[match['distance'].idxmin()]
#            if min_dis_row['distance'] <= 0.4:
#                min_dis_img_path = min_dis_row['identity']
#                base = os.path.basename(min_dis_img_path)
#                face_name = os.path.splitext(base)[0]
#                name = ''.join(filter(lambda x: not x.isdigit(), face_name)).strip()
#
#            face_loc = [match['source_x'][0], match['source_y'][0], match['source_w'][0], match['source_h'][0]]
#            face_bboxes.append(face_loc)
#            recognized_names.append(name)
#    return face_bboxes, recognized_names



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

def process_image_file(image_path):
    frame = cv2.imread(image_path)
    if frame is None or frame.size == 0:
        print("Failed to load image")
        return None, []
    
    face_bboxes, recognized_names = recognize_faces2(frame, known_faces_dir)
    annotated_frame = annotate_frame(frame, face_bboxes, recognized_names)
    return annotated_frame, recognized_names

#def process_image_file(image_path):
#    frame = cv2.imread(image_path)
#    if frame is None:
#        raise ValueError("Failed to load image from path:", image_path)
#
#    annotated_frame, recognized_names = recognize_faces2(frame, 'known_faces')
#    return annotated_frame.tolist(), recognized_names

def update_attendance(recognized_names_global):
    csv_file = 'attendance.csv'
    file_exists = os.path.isfile(csv_file)
    unknown_names=0
    
    attendance_dict = {}
    duplicate_names = {}
    # Read existing names and their attendance times from the CSV file
    if file_exists:
        with open(csv_file, mode='r') as read_file:
            reader = csv.reader(read_file)
            next(reader)
            for row in reader:
                name = row[0]
                attendance_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                attendance_dict[name] = attendance_time
    
    current_time = datetime.now()

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(['Name', 'Attendance Time'])
        
        for name in recognized_names_global:
            if name in attendance_dict:
                last_attendance_time = attendance_dict[name]
                time_diff = current_time - last_attendance_time
                if time_diff >= timedelta(days=0.5):
                    writer.writerow([name, current_time.strftime('%Y-%m-%d %H:%M:%S')])
                    attendance_dict[name] = current_time
                else:
                    if name in duplicate_names:
                        duplicate_names[name] += 1
                    else:
                        duplicate_names[name] = 2

            else:
                if(name!='UNKNOWN'):
                    writer.writerow([name, current_time.strftime('%Y-%m-%d %H:%M:%S')])
                    attendance_dict[name] = current_time
                else:
                    unknown_names+=1
    return unknown_names,duplicate_names

def end_session():
    global cap
    if cap:
        cap.release()
    cv2.destroyAllWindows()
    return {'status': 'success'}
