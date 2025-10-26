from ics import Calendar, Event
from datetime import datetime
import requests
import os
import pytz  # for timezone-aware "now"

# === CONFIG ===
FEED_URL = "https://your.wheniwork.ical.url"  # Replace with your iCal URL
OLD_FILE_PATH = "calendar_old.ics"
MERGED_FILE_PATH = "calendar_merged.ics"
LOCAL_TZ = pytz.timezone("America/New_York")  # Replace with your timezone

def update_calendar():
    # === STEP 1: Fetch new ICS from URL ===
    print("📥 Downloading latest calendar from WhenIWork...")
    response = requests.get(FEED_URL)
    response.raise_for_status()
    new_calendar = Calendar(response.text)

    # === STEP 2: Load old ICS (if exists) ===
    if os.path.exists(OLD_FILE_PATH):
        with open(OLD_FILE_PATH, "r", encoding="utf-8") as f:
            old_calendar = Calendar(f.read())
        print("📁 Loaded previous calendar to keep past events.")
    else:
        old_calendar = Calendar()
        print("📁 No old calendar found. Starting fresh.")

    # === STEP 3: Merge events ===
    now = datetime.now(LOCAL_TZ)  # timezone-aware "now"
    
    merged_events = {
        event.uid: event
        for event in old_calendar.events
        if event.end and event.end >= now  # keep past events only if end exists
    }

    for event in new_calendar.events:
        if event.end and event.end >= now:
            updated_event = Event()
            updated_event.uid = event.uid

            # Clean title
            raw_title = event.name.replace("Shift as", "").strip()
            clean_title = raw_title.split(" at ")[0].strip()
            updated_event.name = clean_title

            # Move description to location
            updated_event.location = event.description.strip() if event.description else ""
            updated_event.description = ""

            # Preserve times and alarms
            updated_event.begin = event.begin
            updated_event.end = event.end
            updated_event.alarms = event.alarms

            merged_events[event.uid] = updated_event

    # === STEP 4: Build final calendar ===
    merged_calendar = Calendar()
    for event in merged_events.values():
        merged_calendar.events.add(event)

    # === STEP 5: Save merged .ics file ===
    with open(MERGED_FILE_PATH, "w", encoding="utf-8") as f:
        f.writelines(merged_calendar.serialize_iter())

    # === STEP 6: Save backup ===
    with open(OLD_FILE_PATH, "w", encoding="utf-8") as f:
        f.writelines(merged_calendar.serialize_iter())

    print(f"✅ Merged calendar saved to: {MERGED_FILE_PATH}")
    print("📅 You can now import or subscribe to this file in Google Calendar.")

if __name__ == "__main__":
    update_calendar()
