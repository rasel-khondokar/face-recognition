import logging
# initialize the log settings
logging.basicConfig(filename='error_daily_log_redis.log', level=logging.INFO, filemode='w')
try:
    import os
    import time
    import pandas as pd
    from functions import redis_client, unix_to_date, unix_to_time, if_dir_not_exists

    dir = "All log"
    if_dir_not_exists(dir)

    all_log = pd.DataFrame(columns=["Date", "Time", "Name", "Face"])
    #print(redis_client.lrange("log", 0, -1))
    while True:
        redis_log_data = redis_client.lpop("log")
        if redis_log_data != None:
            print("Getting data from redis log ")
            data = eval(redis_log_data)
            data['Date'] = unix_to_date(data['Time'])
            data['Time'] = unix_to_time(data['Time'])
            print(data)
            all_log = all_log.append(data, ignore_index=True)
            filename = dir+"/"+"all_log.csv"
            all_log.to_csv(filename, mode='a', header=(not os.path.exists(filename)), index=False)
        else:
            print("Redis log is empty")

        time.sleep(1.0)

except Exception as e:
    logging.exception(str(e))

