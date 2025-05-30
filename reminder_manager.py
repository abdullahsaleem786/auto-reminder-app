import json
import os
from datetime import datetime

DATA_FILE = "data/reminders.json"

def load_reminders():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as file:
        return json.load(file)

def save_reminders(reminders):
    with open(DATA_FILE, "w") as file:
        json.dump(reminders, file, indent=4)

def add_reminder(title, message, time_str):
    reminders = load_reminders()
    reminders.append({
        "title": title,
        "message": message,
        "time": time_str,
        "done": False
    })
    save_reminders(reminders)

def delete_reminder(index):
    reminders = load_reminders()
    reminders.pop(index)
    save_reminders(reminders)

def mark_as_done(index):
    reminders = load_reminders()
    reminders[index]["done"] = True
    save_reminders(reminders)
