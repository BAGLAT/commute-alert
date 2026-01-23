import requests
import datetime
import os
from zoneinfo import ZoneInfo

# ---------------- CONFIG ----------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_APP_TOKEN = os.getenv("PUSHOVER_APP_TOKEN")

ORIGIN = "Hampden Hill, Corballis, Donabate,County Dublin, Ireland"
DESTINATION = "Mastercard South County Business Park, Leopardstown, Dublin 18, Ireland"

TIME_THRESHOLD_MINUTES = 40
NOTIFIED_FILE = "notified_today.txt"
# ----------------------------------------


def already_notified_today():
    today = datetime.date.today().isoformat()
    if os.path.exists(NOTIFIED_FILE):
        with open(NOTIFIED_FILE, "r") as f:
            return f.read().strip() == today
    return False


def mark_notified_today():
    today = datetime.date.today().isoformat()
    with open(NOTIFIED_FILE, "w") as f:
        f.write(today)


def get_travel_time_minutes():
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": ORIGIN,
        "destination": DESTINATION,
        "departure_time": "now",
        "traffic_model": "best_guess",
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] != "OK":
        raise Exception(data.get("error_message", data["status"]))

    leg = data["routes"][0]["legs"][0]
    seconds = leg["duration_in_traffic"]["value"]
    return seconds // 60


def send_notification(minutes):
    url = "https://api.pushover.net/1/messages.json"
    payload = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": "🚗 Commute Alert",
        "message": (
            f"Traffic is light!\n"
            f"Current commute: {minutes} minutes.\n"
            f"Good time to leave."
        )
    }

    requests.post(url, data=payload)


def is_valid_time_window():
    ireland_tz = ZoneInfo("Europe/Dublin")
    now = datetime.datetime.now(tz=ireland_tz)

    # Weekday: Monday=0, Sunday=6
    if now.weekday() >= 5:
        return False

    # Time window: 07:00 – 13:00
    start = now.replace(hour=7, minute=0, second=0, microsecond=0)
    end = now.replace(hour=12, minute=0, second=0, microsecond=0)

    return start <= now < end


def main():
    if not is_valid_time_window():
        return

    if already_notified_today():
        return

    minutes = get_travel_time_minutes()

    if minutes < TIME_THRESHOLD_MINUTES:
        send_notification(minutes)
        mark_notified_today()


if __name__ == "__main__":
    main()
