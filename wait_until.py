import time
from datetime import datetime

def wait_until(target_time):
    now = datetime.now()

    # Get today's target time
    target = now.replace(hour=target_time.hour, minute=target_time.minute, second=target_time.second, microsecond=0)

    # Calculate the difference and sleep for that long
    time_to_wait = (target - now).total_seconds()
    if time_to_wait > 0:
        print(f"Waiting for {time_to_wait} seconds, until {target_time}")
        time.sleep(time_to_wait)
    print("Reached the target time!")
