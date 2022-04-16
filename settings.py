# Redis server
import json

REDIS_URL = 'redis://localhost:6379/0'
# Interval time for same face (in seconds)
INTERVAL_TIME_SAME_FACE = 10
# Preview time of each face (in seconds)
PREVIEW_TIME = 5

# Notification Image size
IMAGE_SIZE = (300, 300)

# Select camera
SELECT_CAM = 0

# There are two mode standard and training mode
APPLICATION_MODE = "training"

# Number of image for training
NUMBER_OF_IMAGE = 10

# Employee ID
FILENAME_EMPS = 'employees.json'
try:
    with open(FILENAME_EMPS) as file:
        EMPLOYEE_ID = json.load(file)
except Exception as e:
    print(e)

def mail_setting():
    active = 1
    fromaddr = "i@gmail.com"
    mail_pass = ""
    toaddr = "n"
    cc = ["rasel@.com", "com"]
    sending_time = ["09:00"]
    return {"Active":active, "From": fromaddr, "Password": mail_pass, "To":toaddr, "Cc":cc, "Times":sending_time}