import logging
import time
import threading
import dlib
# dlib.DLIB_USE_CUDA = True
import face_recognition
import cv2
import numpy as np
import pickle
from settings import SELECT_CAM
from functions import check_if_recent, queue_to_redis, if_dir_not_exists, filename_format

# initialize the log settings
logging.basicConfig(filename='error_standard.log', level=logging.INFO, filemode='w')
try:
    save_face_dir = "Faces"
    if_dir_not_exists(save_face_dir)

    print("[INFO] loading encodings...")
    data = pickle.loads(open("encodings", "rb").read())

    video_capture = cv2.VideoCapture(SELECT_CAM)

    #video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    #video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

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

    known_face_encodings = data['encodings']
    known_face_names = [name.capitalize() for name in data['names']]

    x = 0.0


    time.sleep(3)
    while True:

        frame = thread1.frame
        # Display the resulting image

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]

        # Find all the faces and face encodings in the frame of video
        # face_locations = face_recognition.face_locations(rgb_frame, model="cnn")
        face_location = None
        face_locations = face_recognition.face_locations(rgb_frame, model="cnn")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Loop through each face in this frame of video
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)

            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            # best matched value
            best_matched_value = face_distances[best_match_index]
            # Name
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            # Matched time
            matched_time = time.time()

            # Select area of matched face
            padding = 100
            selected_area_face = frame[top - padding:bottom + padding, left - padding:right + padding]

            data = {"Name": name, "Time": matched_time}

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)

            # Display the resulting image
            dim = (1000, 800)
            resize_frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
            cv2.imshow('Video', resize_frame)

            try:
                if name != "Unknown" and not check_if_recent(data):
                    filename = f'{filename_format(name, matched_time)}.npy'
                    np.save(save_face_dir+"/"+filename, selected_area_face)
                    data["Face"] = filename
                    print(f'Saving to {filename}')
                    queue_to_redis(data)
            except Exception as e:
                logging.exception(str(e))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        print('Time taken', time.process_time() - x)
        x = time.process_time()
        print(dlib.DLIB_USE_CUDA)
    video_capture.release()
    cv2.destroyAllWindows()

except Exception as e:
    logging.exception(str(e))