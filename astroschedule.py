from ics import Calendar, Event
from datetime import datetime
import requests, os
from flask import Flask, send_from_directory

# === CONFIG ===
FEED_URL = "https://app.wheniwork.com/calendar/eacbe0bafebc48a265b8114af6998a69c2c4cb0c.ics"
OLD_FILE_PATH = "calendar_old.ics"
MERGED_FILE_PATH = "calendar_merged.ics"

def update_calendar():
    print("📥 Downloading latest calendar from WhenIWork...")
    response = requests.get(FEED_URL)
    response.raise_for_status()
    new_calendar = Calendar(response.text)

    if os.path.exists(OLD_FILE_PATH):
        with open(OLD_FILE_PATH, "r", encoding="utf-8") as f:
            old_calendar = Calendar(f.read())
        print("Loaded previous calendar to keep past events.")
    else:
        old_calendar = Calendar()
        print("No old calendar found. Starting fresh.")

    now = datetime.now()

    merged_events = {e.uid: e for e in old_calendar.events if e.end < now}

    for event in new_calendar.events:
        if event.end >= now:
            updated_event = Event()
            updated_event.uid = event.uid
            raw_title = event.name.replace("Shift as", "").strip()
            clean_title = raw_title.split(" at ")[0].strip()
            updated_event.name = clean_title
            updated_event.location = event.description.strip() if event.description else ""
            updated_event.description = ""
            updated_event.begin = event.begin
            updated_event.end = event.end
            updated_event.alarms = event.alarms
            merged_events[event.uid] = updated_event

    merged_calendar = Calendar()
    for e in merged_events.values():
        merged_calendar.events.add(e)

    with open(MERGED_FILE_PATH, "w", encoding="utf-8") as f:
        f.writelines(merged_calendar.serialize_iter())

    with open(OLD_FILE_PATH, "w", encoding="utf-8") as f:
        f.writelines(merged_calendar.serialize_iter())

    print("Calendar updated!")

# Run once on startup
update_calendar()

# === Flask server ===
app = Flask(__name__)

@app.route("/calendar.ics")
def serve_calendar():
    return send_from_directory(".", MERGED_FILE_PATH, mimetype="text/calendar")

@app.route("/")
def home():
    return "<h2>WhenIWork Calendar Feed is running!</h2><p>Download: <a href='/calendar.ics'>calendar.ics</a></p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
