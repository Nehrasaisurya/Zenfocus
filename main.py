from newtracker import ActivityTracker
import time
import threading

def track_activity(tracker):
    tracker.track()  

if __name__ == "__main__":
    tracker = ActivityTracker()
    

    tracking_thread = threading.Thread(target=track_activity, args=(tracker,), daemon=True)
    tracking_thread.start()

    try:
        while True:
            time.sleep(1)  
    except KeyboardInterrupt:
        print("Program terminated.")
        tracker.save_log()  