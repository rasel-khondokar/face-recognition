import logging
import time
import os
import pandas as pd
from functions import if_dir_not_exists, get_current_date_time
# initialize the log settings
logging.basicConfig(filename='error_attendance.log', level=logging.INFO, filemode='w')

try:

    dir = "Attendance"
    if_dir_not_exists(dir)

    while True:
        date = get_current_date_time()[1]
        data = pd.read_csv("All log/all_log.csv")
        # Attendance
        attendance = data.groupby(['Date', 'Name']).agg({'Time': ['min', 'max']})
        attendance.columns = ['In Time', 'Out Time']
        attendance = attendance.reset_index()

        # Daily Attendance
        daily_attendance = attendance[attendance['Date'] == date]
        print(daily_attendance)
        # File name
        attendance_filename = dir + "/"+"Attendance.csv"
        daily_attendance_filename = dir + "/"+date+".csv"

        # Save data to csv
        attendance.to_csv(attendance_filename, index=False)
        daily_attendance.to_csv(daily_attendance_filename, index=False)

        time.sleep(3.0)
        print("Getting data from log csv")

except Exception as e:
    logging.exception(str(e))