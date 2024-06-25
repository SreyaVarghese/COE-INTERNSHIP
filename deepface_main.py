from deepface import DeepFace as df
import cv2
import os

known_faces_dir='data_and_installs/images'

def recognize_faces2(frame,dir):
    face_bboxes = []
    recognized_names = []

    name='UNKNOWN'

    matches=df.find(img_path=frame, db_path=dir, model_name='Facenet512',
                            distance_metric='cosine', enforce_detection=True, detector_backend='retinaface', #or centerface
                            align=True, expand_percentage=5, threshold=3)
    if matches and len(matches)>0:
        for i in range (0,len(matches)):
            dataframe=matches[i]
            print(dataframe,'\n\n\n')
            min_dis_row=dataframe.loc[dataframe['distance'].idxmin()]
            if(min_dis_row['distance'] <= 0.5998):
                min_dis_img_path=min_dis_row['identity']
                base=os.path.basename(min_dis_img_path)
                face_name=os.path.splitext(base)[0]
                name=face_name
    
            face_loc=[dataframe['source_x'][0], dataframe['source_y'][0], dataframe['source_w'][0], dataframe['source_h'][0]]
            face_bboxes.append(face_loc)
            recognized_names.append(name)
    return face_bboxes,recognized_names

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    cv2.imshow('Webcam', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('p'):
        captured_frame = frame.copy()        
        face_bboxes, recognized_names = recognize_faces2(captured_frame, known_faces_dir)
        
        # Draw bounding boxes and names on the frame
        for loc, name in zip(face_bboxes, recognized_names):
            x=loc[0]
            y=loc[1]
            w=loc[2]
            h=loc[3]
            cv2.rectangle(captured_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(captured_frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        
        cv2.imshow('Recognized Faces', captured_frame)
        
        cv2.waitKey(0)
        cv2.destroyWindow('Recognized Faces')
    
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()