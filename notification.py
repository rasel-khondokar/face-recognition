import logging
import time
import numpy as np
from functions import redis_client, image_window, beep
# initialize the log settings
logging.basicConfig(filename='error_notification.log', level=logging.INFO, filemode='w')
try:
    while True:
        data = redis_client.lpop("notification")
        if data != None:
            data = eval(data)
            filename = str(data["Face"])
            face = np.load("Faces/" + filename)
            name = data["Name"]
            try:
                beep()
                image_window(face, name)
            except:
                print("Problem in 'Showing face'")
        time.sleep(1)
except Exception as e:
    logging.exception(str(e))
