import json
import re
import time
import datetime
import os
import cv2
import pandas as pd
import redis
import tkinter
from PIL import Image, ImageTk
from pygame import mixer

import settings
from sending_email import send_mail

redis_client = redis.Redis.from_url(settings.REDIS_URL)

def get_current_date_time():
    # Get the time
    local_time = time.localtime()  # get struct_time
    c_month = time.strftime("%m-%Y", local_time)
    c_date = time.strftime("%Y-%m-%d", local_time)
    c_hour_minute = time.strftime("%H:%M", local_time)
    c_hour_minute_second = time.strftime("%H:%M:%S", local_time)
    return c_month, c_date, c_hour_minute, c_hour_minute_second

# check directory if not exists then make directory
def if_dir_not_exists(directory):
    # Check directory exist or not
    if not os.path.exists(directory):
        os.mkdir(directory)

def unix_to_date_time(unix_time):
    time_format = time.localtime(unix_time)
    formatted = time.strftime("%m-%d-%Y, %H:%M:%S", time_format)
    return formatted

def unix_to_date(unix_time):
    time_format = time.localtime(float(unix_time))
    formatted = time.strftime("%Y-%m-%d", time_format)
    return formatted

def unix_to_time(unix_time):
    time_format = time.localtime(float(unix_time))
    formatted = time.strftime("%H:%M:%S", time_format)
    return formatted

def get_previous_date():
    previous_date = datetime.date.today() - datetime.timedelta(1)
    return previous_date

def check_if_recent(data):
    if redis_client.exists(f'last_{data["Name"]}'):
        recognized_face_data = redis_client.get(f'last_{data["Name"]}')
        recognized_face_data = eval(recognized_face_data)
        old_time = recognized_face_data['Time']
        new_time = time.time()
        diff = new_time-old_time
        if diff <= settings.INTERVAL_TIME_SAME_FACE:
            return True
    else:
        redis_client.set(f'last_{data["Name"]}', str(data))
        return False

def queue_to_redis(recognized_face_data):
    data = {"Name": recognized_face_data["Name"], "Time": recognized_face_data["Time"]}
    redis_client.set(f'last_{recognized_face_data["Name"]}', str(data))
    redis_client.rpush("log", str(recognized_face_data))
    redis_client.rpush("notification", str(recognized_face_data))

def save_unknown_face(data):
    data = pd.DataFrame(data, index=[0])
    with open("Unknown.csv", 'a') as f:
        data.to_csv(f, mode='a', header=f.tell() == 0, index=False)

def filename_format(name, matched_time):
    id = settings.EMPLOYEE_ID[name]
    date = unix_to_date(matched_time)
    time = unix_to_time(matched_time)
    filename = re.sub('\W+', '', str(id)+date+time)
    return filename

def image_window(img, name):
    img_width, img_height = settings.IMAGE_SIZE
    b, g, r = cv2.split(img)
    img = cv2.merge((r, g, b))
    img = cv2.resize(img, (img_height, img_width))

    # A root window for displaying objects
    root = tkinter.Tk()
    root.title(name)

    right = root.winfo_screenwidth()
    bottom = root.winfo_screenheight()

    # Window size and position
    root.geometry('%dx%d+%d+%d'%(img_width, img_height,right,bottom))

    # Convert the Image object into a TkPhoto object
    im = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=im)

    # Put it in the display window
    tkinter.Label(root, image=imgtk).pack()

    preview_time = settings.PREVIEW_TIME*1000
    root.after(preview_time, root.destroy)
    root.mainloop()  # Start the GUI

def beep():
   mixer.init()
   mixer.music.load("beep.mp3")
   mixer.music.play()

def make_dir_if_not_exists(file_path):
    dirs = file_path.split('/')
    if dirs:
        path = ''
        for dir in dirs:
            if dir:
                path = path + dir + '/'
                if not os.path.exists(path):
                    os.mkdir(path)

def add_to_emps(name, file):
    dirs = file.split('/')

    try:
        if len(dirs)>=2:
            dir = dirs[:-1]
            make_dir_if_not_exists('/'.join(dir))
    except Exception as e:
        print(e)

    try:
        with open(file, "r") as the_file:
            existing = json.load(the_file)

    except FileNotFoundError as e:
        existing = {name:1}

    if name not in existing:
        id = max(existing.values()) + 1
        existing[name] = id

    with open(file, "w") as the_file:
        json.dump(existing, the_file, indent=4)

    print(f'Saved to {file}')