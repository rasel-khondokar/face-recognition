import json
import logging
import time
import os
import threading
import face_recognition
import cv2
import numpy as np
import pickle
from settings import SELECT_CAM, NUMBER_OF_IMAGE, FILENAME_EMPS, MODEL_NAME
from functions import if_dir_not_exists, add_to_emps
from encode_faces import encode_faces, add_new_with_existing
# initialize the log settings
logging.basicConfig(filename='error_training.log', level=logging.INFO, filemode='w')

try:
    new_face_dir = "New_face"
    if_dir_not_exists(new_face_dir)

    name = input("Enter the employee name : ")

    add_to_emps(name.title(), FILENAME_EMPS)

    if_dir_not_exists(new_face_dir+"/"+name)

    video_capture = cv2.VideoCapture(SELECT_CAM)

    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    class myThread(threading.Thread):

        def __init__(self, threadID, name, counter):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.counter = counter

        def run(self):
            print("Starting " + self.name)
            while True:
                self.ret, self.frame = video_capture.read()


    # Create new threads
    thread1 = myThread(1, "Cam", 1)

    # Start new Threads
    thread1.start()


    x = 0.0


    time.sleep(3)

    count = 0
    while True:

        frame = thread1.frame
        # Display the resulting image

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]
        # Find all the faces and face encodings in the frame of video
        face_location = None
        face_locations = face_recognition.face_locations(rgb_frame,model=MODEL_NAME)
        for (top, right, bottom, left) in face_locations:
            padding = 100
            selected_area_face = frame[top - padding:bottom + padding, left - padding:right + padding]


            try:
                cv2.imwrite(new_face_dir+"/"+name+"/"+str(time.time())+".jpg", selected_area_face)
                count+=1
                time.sleep(.5)
            except Exception as e:
                print(e)

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Display the resulting image
        dim = (1000, 800)
        resize_frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        cv2.imshow('Video', resize_frame)

        #time.sleep(1)

        if cv2.waitKey(1) & 0xFF == ord('q') or count==NUMBER_OF_IMAGE:
            break

        x = time.process_time()

    video_capture.release()
    cv2.destroyAllWindows()

    encode_faces(name)
    add_new_with_existing(name)

except Exception as e:
    logging.exception(str(e))

finally:
    os._exit(0)