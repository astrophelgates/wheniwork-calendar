from flask import Flask, send_file
import os
import subprocess
from threading import Thread
import time

app = Flask(__name__)
ICS_FILE = "calendar_merged.ics"

# Function to update the calendar in background
def update_calendar(interval=3600):  # every hour
    while True:
        subprocess.run(["python", "astroschedule.py"])
        time.sleep(interval)

# Start background thread to update calendar
thread = Thread(target=update_calendar, daemon=True)
thread.start()

@app.route("/calendar.ics")
def serve_calendar():
    if os.path.exists(ICS_FILE):
        return send_file(ICS_FILE, mimetype="text/calendar")
    return "Calendar not ready", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
