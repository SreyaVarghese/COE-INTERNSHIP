from deepface import DeepFace as df
import cv2
import os
import csv
from datetime import datetime,timedelta

known_faces_dir='data_and_installs/aug_images'

def recognize_faces2(frame,dir):
    face_bboxes = []
    recognized_names = []


    matches=df.find(img_path=frame, db_path=dir, model_name='Facenet512',
                            distance_metric='cosine', enforce_detection=False, detector_backend='retinaface',
                            align=True, expand_percentage=5, threshold=3)
    if matches and len(matches)>0:
        for i in range (0,len(matches)):
            name='UNKNOWN'
            dataframe=matches[i]
            print(dataframe.head(3),'\n\n\n')
            min_dis_row=dataframe.loc[dataframe['distance'].idxmin()]
            if(min_dis_row['distance'] <= 0.4):
                min_dis_img_path=min_dis_row['identity']
                base=os.path.basename(min_dis_img_path)
                face_name=os.path.splitext(base)[0]
                name = ''.join(filter(lambda x: not x.isdigit(), face_name))
                name=name.strip()
    
            face_loc=[dataframe['source_x'][0], dataframe['source_y'][0], dataframe['source_w'][0], dataframe['source_h'][0]]
            face_bboxes.append(face_loc)
            recognized_names.append(name)
    return face_bboxes,recognized_names

def update_attendance(names):
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
        
        for name in names:
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

#for live web cam

# cap = cv2.VideoCapture(0)

# while cap.isOpened():
#     success, frame = cap.read()
#     cv2.imshow('Webcam', frame)
    
#     key = cv2.waitKey(1) & 0xFF
#     if key == ord('p'):
#         captured_frame = frame.copy()
        
#         # Recognize faces in the captured frame
#         face_bboxes, recognized_names = recognize_faces2(captured_frame, known_faces_dir)
        
#         for loc, name in zip(face_bboxes, recognized_names):           
#             x=loc[0]
#             y=loc[1]
#             w=loc[2]
#             h=loc[3]
#             box_color=(0,255,0)
#             thick=2
#             font_color=(0,0,255)
#             if(name =='UNKNOWN'):
#                 box_color=(0,0,255)
#                 thick=3
#                 font_color=(0,100,255)
            
#             cv2.rectangle(captured_frame, (x, y), (x + w, y + h), box_color, thick)
#             cv2.putText(captured_frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, font_color, 1)
        
#         # Display the frame with bounding boxes and names
#         cv2.imshow('Recognized Faces', captured_frame)

#         while True:
#             mark_attendance= cv2.waitKey(1) & 0xFF
#             if mark_attendance== ord('u'):
#                 unknown_names,duplicate_names=update_attendance(recognized_names)
#                 if(unknown_names==0):
#                     print('first image attendance marked')
#                 else:
#                     print('{} unknown students in first image and rest marked'.format(unknown_names))
                
#                 print(duplicate_names)
#                 if len(duplicate_names)!=0:
#                     duplicate_frame=frame.copy()
#                     # duplicate_frame=cv2.resize(duplicate_frame,(1080,1150))
#                     for loc, name in zip(face_bboxes, recognized_names):           
#                         x=loc[0]
#                         y=loc[1]
#                         w=loc[2]
#                         h=loc[3]
#                         box_color=(0,255,0)
#                         thick=2
#                         font_color=(255,0,0)
#                         if(name =='UNKNOWN'):
#                             box_color=(0,0,255)
#                             thick=3
#                             font_color=(0,100,255)
#                         if name in duplicate_names:
#                             box_color=(0,0,0)
#                             font_color=(0,255,0)

#                         cv2.rectangle(duplicate_frame, (x, y), (x + w, y + h), box_color, thick)
#                         cv2.putText(duplicate_frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, font_color, 1)
#                     cv2.imshow('duplicate',duplicate_frame)
#                     while True:
#                         duplicate_key=cv2.waitKey(1) & 0xFF
#                         if(duplicate_key==27):
#                             break
#                 break

#             elif mark_attendance==27:
#                 break
        
#         cv2.destroyWindow('Recognized Faces')
    
#     # Press 'esc' to quit the webcam loop
#     if key == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()

#for group images

test_img='data_and_installs/test_images/JAYPEE_FAM(1).jpeg'

captured_frame = cv2.imread(test_img)
face_bboxes, recognized_names = recognize_faces2(captured_frame, known_faces_dir)

for loc, name in zip(face_bboxes, recognized_names):           
    x=loc[0]
    y=loc[1]
    w=loc[2]
    h=loc[3]
    box_color=(0,255,0)
    thick=2
    font_color=(0,0,255)
    if(name =='UNKNOWN'):
        box_color=(0,0,255)
        thick=3
        font_color=(0,100,255)
    
    cv2.rectangle(captured_frame, (x, y), (x + w, y + h), box_color, thick)
    cv2.putText(captured_frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, font_color, 1)
        

cv2.imshow('Recognized Faces', captured_frame)
while True:
    mark_attendance= cv2.waitKey(1) & 0xFF
    if mark_attendance== ord('u'):
        unknown_names,duplicate_names=update_attendance(recognized_names)

        if(unknown_names==0):
            print('first image attendance marked')
        else:
            print('{} unknown students in first image and rest marked'.format(unknown_names))

        print(duplicate_names)

        if len(duplicate_names)!=0:
            duplicate_frame=cv2.imread(test_img)
            # duplicate_frame=cv2.resize(duplicate_frame,(1080,1150))
            for loc, name in zip(face_bboxes, recognized_names):           
                x=loc[0]
                y=loc[1]
                w=loc[2]
                h=loc[3]
                box_color=(0,255,0)
                thick=2
                font_color=(255,0,0)
                if(name =='UNKNOWN'):
                    box_color=(0,0,255)
                    thick=3
                    font_color=(0,100,255)
                if name in duplicate_names:
                    box_color=(0,0,0)
                    font_color=(0,255,0)

                cv2.rectangle(duplicate_frame, (x, y), (x + w, y + h), box_color, thick)
                cv2.putText(duplicate_frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, font_color, 1)
            cv2.imshow('duplicate',duplicate_frame)
            while True:
                duplicate_key=cv2.waitKey(1) & 0xFF
                if(duplicate_key==27):
                    break

        break

    elif mark_attendance==27:
        break
        
cv2.destroyWindow('Recognized Faces')