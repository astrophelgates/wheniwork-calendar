from flask import Flask, send_file
import os

app = Flask(__name__)

ICS_FILE = "calendar_merged.ics"

@app.route("/calendar.ics")
def serve_calendar():
    if os.path.exists(ICS_FILE):
        return send_file(ICS_FILE, mimetype="text/calendar")
    else:
        return "Calendar not ready", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
