import requests
import datetime
import os

import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_APP_TOKEN = os.getenv("PUSHOVER_APP_TOKEN")


# ---------------- CONFIG ----------------
GOOGLE_API_KEY = "AIzaSyCVx6fCzmq2_LtqgfSzP6ep-aUouGeLWAs"

PUSHOVER_USER_KEY = "unj7j6nwm5wjivmzkd5sezy9s95omq"
PUSHOVER_APP_TOKEN = "akkacpekepszut77ha5xore3ysoo1n"

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
        "origin": "Hampden Hill, Corballis, Donabate,County Dublin, Ireland",
        "destination": "Mastercard South County Business Park, Leopardstown, Dublin 18, Ireland",
        "departure_time": "now",
        "traffic_model": "best_guess",
        "key": "AIzaSyCVx6fCzmq2_LtqgfSzP6ep-aUouGeLWAs"
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
        "token": "akkacpekepszut77ha5xore3ysoo1n",
        "user": "unj7j6nwm5wjivmzkd5sezy9s95omq",
        "title": "🚗 Commute Alert",
        "message": f"Traffic is light! Travel time is {minutes} minutes.\nGood time to leave.",
        "priority": 0
    }

    response = requests.post(url, data=payload)
    result = response.json()
    
    if result.get("status") == 1:
        print(f"✅ Notification sent successfully! Travel time: {minutes} minutes")
    else:
        print(f"❌ Failed to send notification: {result.get('errors', 'Unknown error')}")
        print(f"Response: {result}")


def main():
    now = datetime.datetime.now()

    # Only between 7 AM and 12 PM
    # if not (7 <= now.hour < 12):
    #     return

    # if already_notified_today():
    #     return

    try:
        minutes = get_travel_time_minutes()
        print(f"📍 Current travel time: {minutes} minutes (threshold: {TIME_THRESHOLD_MINUTES} minutes)")
        
        if minutes < TIME_THRESHOLD_MINUTES:
            print(f"✅ Travel time is below threshold! Sending notification...")
            send_notification(minutes)
            mark_notified_today()
        else:
            print(f"⏳ Travel time is {minutes} minutes (>= {TIME_THRESHOLD_MINUTES} minutes). No notification sent.")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
